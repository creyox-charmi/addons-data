# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # SmartPosti fields
    smartposti_service_type = fields.Selection(
        [("pudo", "Parcel Machines"), ("po", "Post Offices")],
        string="SmartPosti Service Type",
        copy=False,
    )

    smartposti_place_id = fields.Many2one(
        "smartposti.place", string="Selected Pickup Point", copy=False
    )

    # Omniva fields
    omniva_delivery_channel = fields.Selection(
        [
            ("COURIER", "Courier"),
            ("POST_OFFICE", "Post Office"),
            ("PARCEL_MACHINE", "Parcel Machine"),
        ],
        string="Omniva Delivery Channel",
        copy=False,
    )

    omniva_location_id = fields.Many2one(
        "omniva.location", string="Omniva Pickup Location", copy=False
    )

    def _action_confirm(self):
        """Override to transfer data to picking"""
        result = super(SaleOrder, self)._action_confirm()

        # Transfer SmartPosti data
        for order in self:
            if order.carrier_id and order.carrier_id.delivery_type == "smartposti":
                pickings = order.picking_ids.filtered(
                    lambda p: p.picking_type_code == "outgoing"
                    and not p.smartposti_place_id
                )
                if pickings and order.smartposti_place_id:
                    pickings.write(
                        {"smartposti_place_id": order.smartposti_place_id.id}
                    )

            # Transfer Omniva data
            if order.carrier_id and order.carrier_id.delivery_type == "omniva":
                pickings = order.picking_ids.filtered(
                    lambda p: p.picking_type_code == "outgoing"
                )
                if pickings and order.omniva_location_id:
                    for picking in pickings:
                        picking.write(
                            {
                                "note": f"Omniva {order.omniva_delivery_channel}: {order.omniva_location_id.name}, {order.omniva_location_id.address}"
                            }
                        )

        return result

    @api.depends("order_line.price_total", "order_line.price_subtotal", "carrier_id")
    def _compute_amount_delivery(self):
        """Override to handle dynamic pricing for SmartPosti and Omniva"""

        super(SaleOrder, self)._compute_amount_delivery()
        for order in self.filtered(lambda o: o.website_id and o.carrier_id):

            if order.carrier_id.delivery_type == "omniva":
                partner_country = order.partner_id.country_id
                if not partner_country:
                    continue

                locations_exist = self.env["omniva.location"].search_count(
                    [("country", "=", partner_country.code), ("active", "=", True)],
                    limit=1,
                )

                if not locations_exist:
                    continue

                delivery_channel = order.omniva_delivery_channel or "COURIER"
                if request and hasattr(request, "session"):
                    delivery_channel = request.session.get(
                        "omniva_delivery_channel", delivery_channel
                    )
                    if delivery_channel != order.omniva_delivery_channel:
                        order.omniva_delivery_channel = delivery_channel

                company = order.company_id

                country_price = self.env["omniva.country.price"].search(
                    [
                        ("company_id", "=", company.id),
                        ("delivery_channel", "=", delivery_channel),
                        ("country_id", "=", partner_country.id),
                    ],
                    limit=1,
                )

                if country_price:
                    target_price = country_price.price
                else:
                    if delivery_channel == "COURIER":
                        target_price = company.omniva_courier_price or 0.00
                    elif delivery_channel == "PARCEL_MACHINE":
                        target_price = company.omniva_parcel_machine_price or 0.50
                    else:
                        target_price = company.omniva_post_office_price or 0.00

                delivery_lines = order.order_line.filtered("is_delivery")
                if delivery_lines:
                    for line in delivery_lines:
                        if line.price_unit != target_price:
                            line.write({"price_unit": target_price})

                        # ADD THIS: Update description with location name
                        if order.omniva_location_id and delivery_channel in [
                            "PARCEL_MACHINE",
                            "POST_OFFICE",
                        ]:
                            location = order.omniva_location_id
                            location_type_label = (
                                "Parcel Machine"
                                if delivery_channel == "PARCEL_MACHINE"
                                else "Post Office"
                            )
                            new_description = f"Omniva \n{location_type_label}: {location.name}\nAddress: {location.address}, {location.city}"
                            if line.name != new_description:
                                line.write({"name": new_description})

                    if (
                        order.website_id.show_line_subtotals_tax_selection
                        == "tax_excluded"
                    ):
                        order.amount_delivery = sum(
                            delivery_lines.mapped("price_subtotal")
                        )
                    else:
                        order.amount_delivery = sum(
                            delivery_lines.mapped("price_total")
                        )
