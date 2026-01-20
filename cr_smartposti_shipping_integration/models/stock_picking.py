# -*- coding: utf-8 -*-
"""SmartPosti Stock Picking Extensions"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    smartposti_place_id = fields.Many2one(
        "smartposti.place",
        string="Pickup Point",
        help="SmartPosti pickup location",
        copy=False,
    )
    smartposti_door_code = fields.Char(
        string="Door Code",
        help="SmartPosti parcel terminal door code",
        readonly=True,
        copy=False,
    )
    smartposti_size = fields.Selection(
        [
            ("XS", "Extra Small"),
            ("S", "Small"),
            ("M", "Medium"),
            ("L", "Large"),
            ("XL", "Extra Large"),
        ],
        string="Package Size",
        copy=False,
    )
    smartposti_express = fields.Boolean(
        string="Express Delivery", help="Use SmartPosti Express service", copy=False
    )
    smartposti_temperature_sensitive = fields.Boolean(
        string="Temperature Sensitive",
        help="Package requires temperature control",
        copy=False,
    )
    smartposti_barcode = fields.Char(
        string="Tracking Barcode",
        help="SmartPosti tracking number",
        readonly=True,
        copy=False,
    )

    @api.onchange("carrier_id")
    def _onchange_carrier_smartposti(self):
        """Set defaults when SmartPosti carrier selected"""
        if not self.carrier_id or self.carrier_id.delivery_type != "smartposti":
            return

        # Set default size
        self.smartposti_size = self.carrier_id.smartposti_default_size

        # Try to find nearby place
        if not self.smartposti_place_id and self.partner_id:
            self._set_default_smartposti_place()

    @api.onchange("partner_id")
    def _onchange_partner_smartposti(self):
        """Update place when partner changes"""
        if (
            self.carrier_id
            and self.carrier_id.delivery_type == "smartposti"
            and self.partner_id
        ):
            self._set_default_smartposti_place()

    def _set_default_smartposti_place(self):
        """Find and set default SmartPosti place based on partner location"""
        if not self.carrier_id or not self.partner_id:
            return

        domain = [
            ("country", "=", self.carrier_id.smartposti_country),
            ("active", "=", True),
        ]

        # Try to match by postal code first, then city
        if self.partner_id.zip:
            domain.append(("postal_code", "=", self.partner_id.zip))
        elif self.partner_id.city:
            domain.append(("city", "ilike", self.partner_id.city))

        place = self.env["smartposti.place"].search(domain, limit=1)
        if place:
            self.smartposti_place_id = place

    def button_validate(self):
        """Override validation to create SmartPosti shipment"""
        res = super(StockPicking, self).button_validate()

        # Process outgoing SmartPosti shipments
        smartposti_pickings = self.filtered(
            lambda p: (
                p.carrier_id
                and p.carrier_id.delivery_type == "smartposti"
                and p.picking_type_code == "outgoing"
                and not p.smartposti_barcode
            )
        )

        for picking in smartposti_pickings:
            try:
                picking.smartposti_send_shipping()
            except Exception as e:
                raise ValidationError(
                    _("Failed to create SmartPosti shipment: %s") % str(e)
                )

        return res

    def smartposti_send_shipping(self):
        """Create SmartPosti shipment using carrier method"""
        self.ensure_one()

        if not self.carrier_id or self.carrier_id.delivery_type != "smartposti":
            return

        # Use carrier's send_shipping method
        result = self.carrier_id.send_shipping(self)

        if result and result[0].get("tracking_number"):
            # Tracking info already set by carrier method
            self.message_post(
                body=_("SmartPosti shipment created successfully"),
                subject=_("Shipment Created"),
            )

    def open_website_url(self):
        """Open tracking URL in browser"""
        if self.carrier_id and self.carrier_id.delivery_type == "smartposti":
            if not self.smartposti_barcode:
                return False

            tracking_url = f"https://www.smartpost.ee/private/tracking?barcode={self.smartposti_barcode.strip()}"

            return {
                "type": "ir.actions.act_url",
                "name": _("Shipment Tracking"),
                "target": "new",
                "url": tracking_url,
            }

        return super(StockPicking, self).open_website_url()

    def action_smartposti_track_shipment(self):
        """Display detailed tracking information"""
        self.ensure_one()

        if not self.smartposti_barcode:
            raise UserError(_("No tracking number available"))

        try:
            client = self.carrier_id._get_smartposti_client()
            tracking_data = client.track_shipment(barcode=self.smartposti_barcode)

            if tracking_data.get("error"):
                raise UserError(_("Tracking Error: %s") % tracking_data["error"])

            tracking_info = self._format_tracking_info(tracking_data)

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Tracking Information"),
                    "message": tracking_info,
                    "type": "info",
                    "sticky": True,
                },
            }

        except Exception as e:
            raise UserError(_("Failed to retrieve tracking: %s") % str(e))

    def _format_tracking_info(self, tracking_data):
        """Format tracking data for display

        Args:
            tracking_data: API tracking response

        Returns:
            str: Formatted HTML tracking information
        """
        item = tracking_data.get("item", [{}])
        if isinstance(item, list):
            item = item[0] if item else {}

        events = [
            ("generated", _("Order generated")),
            ("sourcein", _("Collected from sender")),
            ("sourceout", _("Dispatched from origin")),
            ("termin", _("Arrived at sorting facility")),
            ("termout", _("Departed from sorting")),
            ("destinationin", _("Arrived at destination")),
            ("destinationout", _("Delivered")),
            ("returnin", _("Return initiated")),
            ("returnout", _("Return collected")),
        ]

        tracking_lines = []
        for event_key, event_desc in events:
            if item.get(event_key):
                tracking_lines.append(f"{event_desc}: {item[event_key]}")

        return (
            "<br/>".join(tracking_lines)
            if tracking_lines
            else _("No tracking data available")
        )
