# -*- coding: utf-8 -*-
"""SmartPosti Delivery Carrier Integration"""

import base64
import json
import logging
from odoo.http import request

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from .smartposti_client import SmartPostiClient

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("smartposti", "SmartPosti")],
        ondelete={"smartposti": "set default"},
    )

    def _get_smartposti_client(self):
        """Initialize and return SmartPosti API client"""
        self.ensure_one()
        if self.delivery_type != "smartposti":
            raise UserError(_("This method is only available for SmartPosti carriers"))

        company = self.env.company

        if not company.smartposti_base_url:
            raise UserError(
                _("SmartPosti API Base URL is not configured in Company settings")
            )

        if not company.smartposti_api_key or not company.smartposti_gateway_secret:
            raise UserError(
                _("SmartPosti API credentials are not configured in Company settings")
            )

        return SmartPostiClient(
            base_url=company.smartposti_base_url,
            api_key=company.smartposti_api_key,
            gateway_secret=company.smartposti_gateway_secret,
        )

    def _get_smartposti_country(self):
        """Get country for this carrier (carrier override or company default)"""
        self.ensure_one()
        return (
            self.env.company.smartposti_default_country
            or self.env.company.country_code
            or "EE"
        )

    @staticmethod
    def _clean_phone(phone_str):
        """Clean and validate phone number

        Args:
            phone_str: Phone number string to clean

        Returns:
            int: Cleaned phone number or 0 if invalid
        """
        if not phone_str:
            return 0

        digits = "".join(c for c in str(phone_str) if c.isdigit())

        if len(digits) < 7:
            _logger.warning(f"Phone number too short: {phone_str}")
            return 0

        try:
            return int(digits)
        except ValueError:
            _logger.warning(f"Invalid phone number: {phone_str}")
            return 0

    def _validate_shipment_data(self, picking):
        """Validate required data before creating shipment

        Args:
            picking: stock.picking record

        Raises:
            UserError: If validation fails
        """
        partner = picking.partner_id
        company = self.env.company

        if not partner.name:
            raise UserError(_("Recipient name is required"))
        if not (partner.phone or partner.mobile):
            raise UserError(_("Recipient phone number is required"))
        if not partner.email:
            raise UserError(_("Recipient email is required"))
        if not picking.smartposti_place_id:
            raise UserError(_("SmartPosti pickup point must be selected"))

        # Additional validation for door code service
        if company.smartposti_use_door_code:
            if not company.name:
                raise UserError(_("Company name is required for door code service"))
            if not company.phone:
                raise UserError(_("Company phone is required for door code service"))

    def _prepare_smartposti_order_data(self, picking):
        """Prepare order payload for SmartPosti API

        Args:
            picking: stock.picking record

        Returns:
            dict: API order payload
        """
        self.ensure_one()
        if self.delivery_type != "smartposti":
            raise UserError(_("This method is only for SmartPosti carriers"))

        # Validate data
        self._validate_shipment_data(picking)

        partner = picking.partner_id
        company = self.env.company
        country = self._get_smartposti_country()

        # Base order item
        item = {
            "reference": picking.name or f"OP/{picking.origin or 'N/A'}",
            "source": {"country": country},
            "recipient": {
                "name": partner.name,
                "phone": self._clean_phone(partner.phone or partner.mobile),
                "email": partner.email,
            },
            "destination": {
                "country": country,
                "place_id": picking.smartposti_place_id.place_id,
            },
            "additionalservices": {"labelprinted": "true"},
        }

        # Add sender info if door code service enabled (from company settings)
        if company.smartposti_use_door_code:
            item["sender"] = {
                "name": company.name,
                "phone": self._clean_phone(company.phone),
                "email": company.email or "",
                "address": company.street or "",
                "city": company.city or "",
                "postalcode": company.zip or "",
                "country": company.country_id.code or country,
            }

            # Add package details (required with sender)
            item["size"] = (
                picking.smartposti_size or company.smartposti_default_size or "M"
            )

            # Calculate weight
            total_weight = (
                sum(
                    line.product_id.weight * line.product_uom_qty
                    for line in picking.move_lines
                )
                or 0.1
            )
            item["weight"] = str(round(total_weight, 2))

        # Add additional services from company settings
        services = item["additionalservices"]

        if company.smartposti_enable_express:
            services["express"] = "true"
        if company.smartposti_enable_id_check:
            services["idcheck"] = "true"
        if company.smartposti_enable_age_check:
            services["agecheck"] = "true"
        if company.smartposti_enable_cod:
            services["paidbyrecipient"] = "true"
        if company.smartposti_notification_email:
            services["notifyemail"] = company.smartposti_notification_email
        if company.smartposti_notification_phone:
            services["notifyphone"] = company.smartposti_notification_phone
        if picking.smartposti_temperature_sensitive:
            services["temperaturesensitive"] = "true"

        order_data = {"orders": {"item": [item]}}

        return order_data

    def _process_order_response(self, response, picking):
        """Process API response and update picking

        Args:
            response: API response dict
            picking: stock.picking record

        Returns:
            str: Barcode/tracking number
        """
        if response.get("error"):
            raise ValidationError(_("SmartPosti API Error: %s") % response["error"])

        # Extract order data
        order_item = response.get("orders", {}).get("item", {})
        if isinstance(order_item, list):
            order_item = order_item[0] if order_item else {}

        barcode = order_item.get("barcode")
        if not barcode:
            raise ValidationError(_("No tracking barcode received from SmartPosti"))

        # Update picking
        picking.write({"smartposti_barcode": barcode, "carrier_tracking_ref": barcode})

        # Store door code if available
        door_code = None
        if isinstance(order_item.get("sender"), dict):
            door_code = order_item.get("sender", {}).get("doorcode")

        if door_code:
            picking.smartposti_door_code = door_code
            picking.message_post(
                body=_("SmartPosti Door Code: %s") % door_code,
                subject=_("Shipment Created"),
            )

        return barcode

    def _generate_and_attach_label(self, picking, barcode):
        """Generate shipping label and attach to picking

        Args:
            picking: stock.picking record
            barcode: Tracking barcode
        """
        try:
            company = self.env.company
            client = self._get_smartposti_client()

            # Use company label format setting
            label_format = company.smartposti_label_format or "A5"
            label_response = client.get_labels([barcode], label_format)

            if not label_response.get("binary"):
                raise ValidationError(_("No PDF label in API response"))

            # Create attachment
            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"SmartPosti-Label-{barcode}.pdf",
                    "type": "binary",
                    "datas": base64.b64encode(label_response["binary"]),
                    "res_model": "stock.picking",
                    "res_id": picking.id,
                    "mimetype": "application/pdf",
                    "description": f"SmartPosti label for {picking.name}",
                }
            )

            # Post message with label
            picking.message_post(
                body=_("SmartPosti shipment created with tracking: %s") % barcode,
                attachment_ids=[attachment.id],
            )

        except Exception as e:
            _logger.warning(f"Label generation failed for {barcode}: {str(e)}")
            picking.message_post(
                body=_("Warning: Shipment created but label generation failed: %s")
                % str(e),
                subject=_("Label Generation Warning"),
            )

    def smartposti_send_shipping(self, pickings):
        """Send shipments to SmartPosti and generate labels

        Args:
            pickings: stock.picking recordset

        Returns:
            list: Shipping results
        """
        results = []
        client = self._get_smartposti_client()

        for picking in pickings:
            try:
                # Prepare and create order
                order_data = self._prepare_smartposti_order_data(picking)
                response = client.create_order(order_data)

                # Process response
                barcode = self._process_order_response(response, picking)

                # Generate label
                self._generate_and_attach_label(picking, barcode)

                results.append({"tracking_number": barcode, "exact_price": 0.0})

            except Exception as e:
                _logger.error(f"Shipment creation failed for {picking.name}: {str(e)}")
                raise UserError(_("Failed to create shipment: %s") % str(e))

        return results

    def smartposti_get_tracking_link(self, picking):
        """Generate tracking URL

        Args:
            picking: stock.picking record

        Returns:
            str: Tracking URL or False
        """
        if not picking.carrier_tracking_ref:
            return False
        return f"https://www.smartpost.ee/private/tracking?barcode={picking.carrier_tracking_ref}"

    def smartposti_cancel_shipment(self, picking):
        """Handle shipment cancellation

        Note: SmartPosti API doesn't provide automated cancellation
        """
        picking.message_post(
            body=_(
                "SmartPosti cancellation requires manual intervention. Contact SmartPosti support."
            ),
            subject=_("Cancellation Required"),
        )
        return True


    def smartposti_rate_shipment(self, order):
        """Rate shipment based on session service type and partner country"""
        self.ensure_one()
        company = self.env.company

        partner = order.partner_id
        partner_country = partner.country_id

        if not partner_country:
            return {
                'success': False,
                'price': 0.0,
                'error_message': _('Partner country is not set. Please update delivery address.'),
                'warning_message': False
            }

        places_exist = self.env['smartposti.place'].search_count([
            ('country', '=', partner_country.code),
            ('active', '=', True)
        ], limit=1)

        if not places_exist:
            return {
                'success': False,
                'price': 0.0,
                'error_message': _('SmartPosti delivery is not available for %s') % partner_country.name,
                'warning_message': False
            }

        service_type = 'pudo'
        if request and hasattr(request, 'session'):
            service_type = request.session.get('smartposti_service_type', 'pudo')

        country_price = self.env['smartposti.country.price'].search([
            ('company_id', '=', company.id),
            ('service_type', '=', service_type),
            ('country_id', '=', partner_country.id)
        ], limit=1)

        if country_price:
            price = country_price.price
        else:
            if service_type == 'courier':
                price = company.smartposti_courier_price or 5.50
            else:
                price = company.smartposti_pudo_price or 3.50

        # ADD TAX CALCULATION
        if self.product_id and self.product_id.taxes_id:
            fiscal_position = order.fiscal_position_id
            taxes = fiscal_position.map_tax(self.product_id.taxes_id) if fiscal_position else self.product_id.taxes_id

            if taxes:
                tax_ids = taxes.filtered(lambda t: not t.price_include)
                if tax_ids:
                    tax_amount = tax_ids.compute_all(
                        price,
                        order.currency_id,
                        1.0,
                        product=self.product_id,
                        partner=order.partner_shipping_id
                    )['total_included'] - price
                    price += tax_amount

        return {
            'success': True,
            'price': price,
            'error_message': False,
            'warning_message': False
        }


    def action_sync_smartposti_places(self):
        """Sync pickup places - delegate to company action"""
        self.ensure_one()
        if self.delivery_type != "smartposti":
            raise UserError(_("This action is only for SmartPosti carriers"))

        # Use company's sync method
        return self.env.company.action_sync_smartposti_places()

    # Override base methods
    def send_shipping(self, pickings):
        """Override base send_shipping"""
        if self.delivery_type == "smartposti":
            return self.smartposti_send_shipping(pickings)
        return super().send_shipping(pickings)

    def get_tracking_link(self, picking):
        """Override base get_tracking_link"""
        if self.delivery_type == "smartposti":
            return self.smartposti_get_tracking_link(picking)
        return super().get_tracking_link(picking)

    def cancel_shipment(self, picking):
        """Override base cancel_shipment"""
        if self.delivery_type == "smartposti":
            return self.smartposti_cancel_shipment(picking)
        return super().cancel_shipment(picking)

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


