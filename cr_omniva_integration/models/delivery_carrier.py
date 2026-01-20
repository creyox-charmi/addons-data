# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("omniva", "Omniva")], ondelete={"omniva": "set default"}
    )

    # Omniva specific fields
    omniva_main_service = fields.Selection(
        [("PARCEL", "Parcel"), ("LETTER", "Letter")],
        string="Main Service",
        default="PARCEL",
    )

    omniva_delivery_channel = fields.Selection(
        [
            ("COURIER", "Courier"),
            ("POST_OFFICE", "Post Office"),
            ("PARCEL_MACHINE", "Parcel Machine"),
        ],
        string="Delivery Channel",
        default="COURIER",
    )

    omniva_service_package = fields.Selection(
        [("STANDARD", "Standard"), ("ECONOMY", "Economy"), ("PREMIUM", "Premium")],
        string="Service Package",
        default="STANDARD",
    )

    omniva_label_format = fields.Selection(
        [("A4", "A4"), ("A6", "A6")], string="Label Format", default="A4"
    )

    omniva_default_package_id = fields.Many2one(
        "stock.package.type", string="Default Package Type"
    )

    def omniva_rate_shipment(self, order):
        """Calculate shipping rate based on selected delivery channel and country"""
        self.ensure_one()
        company = self.env.company

        # Get partner country
        partner = order.partner_id
        partner_country = partner.country_id

        if not partner_country:
            return {
                "success": False,
                "price": 0.0,
                "error_message": _(
                    "Partner country is not set. Please update delivery address."
                ),
                "warning_message": False,
            }

        # Check if locations exist for partner's country
        locations_exist = self.env["omniva.location"].search_count(
            [("country", "=", partner_country.code), ("active", "=", True)], limit=1
        )

        if not locations_exist:
            return {
                "success": False,
                "price": 0.0,
                "error_message": _("Omniva delivery is not available for %s")
                % partner_country.name,
                "warning_message": False,
            }

        # Get delivery channel from session
        delivery_channel = "COURIER"
        if request and hasattr(request, "session"):
            delivery_channel = request.session.get("omniva_delivery_channel", "COURIER")

        # Find country-specific price
        country_price = self.env["omniva.country.price"].search(
            [
                ("company_id", "=", company.id),
                ("delivery_channel", "=", delivery_channel),
                ("country_id", "=", partner_country.id),
            ],
            limit=1,
        )

        if country_price:
            price = country_price.price
        else:
            # Fallback to default prices
            if delivery_channel == "COURIER":
                price = company.omniva_courier_price or 0.00
            elif delivery_channel == "PARCEL_MACHINE":
                price = company.omniva_parcel_machine_price or 0.50
            else:
                price = company.omniva_post_office_price or 0.00

        return {
            "success": True,
            "price": price,
            "error_message": False,
            "warning_message": False,
        }

    def _calculate_price_with_tax(self, base_price, order):
        """Calculate price including tax if configured"""
        self.ensure_one()

        if not self.product_id or not self.product_id.taxes_id:
            return base_price

        # Get fiscal position mapped taxes
        fpos = order.fiscal_position_id
        taxes = self.product_id.taxes_id

        if fpos:
            taxes = fpos.map_tax(taxes)

        if not taxes:
            return base_price

        # Check tax configuration
        for tax in taxes:
            if tax.price_include:
                # Price already includes tax, return as-is
                return base_price
            elif tax.amount_type == 'percent':
                # Add tax to base price
                tax_amount = base_price * (tax.amount / 100)
                base_price += tax_amount

        return base_price


    def omniva_send_shipping(self, pickings):
        """Send shipment to Omniva and return tracking info.

        This method is called by Odoo's standard delivery flow.
        """
        res = []

        for picking in pickings:
            try:
                # Call the picking's omniva_send_shipping method
                picking.omniva_send_shipping()

                # Return the expected format for Odoo
                res.append(
                    {
                        "exact_price": 0.0,  # You can calculate actual price here
                        "tracking_number": picking.omniva_barcode or False,
                    }
                )
            except Exception as e:
                raise UserError(
                    _("Failed to create Omniva shipment for %s: %s")
                    % (picking.name, str(e))
                )

        return res

    def omniva_get_tracking_link(self, picking):
        """Get tracking link for Omniva shipment."""
        if picking.omniva_barcode:
            return f"https://www.omniva.ee/track?barcode={picking.omniva_barcode}"
        return False

    def omniva_cancel_shipment(self, pickings):
        """Cancel Omniva shipment.

        Note: As per Omniva API docs, shipments can only be cancelled/modified
        if they are in REGISTERED status. This should be done via Omniva portal.
        """
        pickings.message_post(
            body=_(
                "Omniva shipments must be cancelled through the Omniva portal or by contacting support."
            )
        )


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = "choose.delivery.carrier"

    def _get_shipment_rate(self):
        """Override to handle Omniva rate calculation."""
        if self.delivery_type == "omniva":
            return self.carrier_id.omniva_rate_shipment(self.order_id)
        return super()._get_shipment_rate()
