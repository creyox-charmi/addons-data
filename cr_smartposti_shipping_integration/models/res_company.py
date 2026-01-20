# -*- coding: utf-8 -*-
"""SmartPosti Company Configuration"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    # API Configuration
    smartposti_api_key = fields.Char(
        string="SmartPosti API Key", help="SmartPosti API authentication key"
    )
    smartposti_gateway_secret = fields.Char(
        string="SmartPosti Gateway Secret",
        help="SmartPosti gateway secret for API authentication",
    )
    smartposti_base_url = fields.Char(
        string="SmartPosti API Base URL",
        default="https://gateway.demo.posti.fi/smartpost/api/ext/v1",
        help="SmartPosti API endpoint URL",
        store=True,
    )
    smartposti_environment = fields.Selection(
        [("demo", "Demo/Test Environment"), ("live", "Live/Production Environment")],
        string="SmartPosti Environment",
        default="demo",
        help="Select API environment",
    )

    # Default Service Configuration
    smartposti_default_country = fields.Selection(
        [("EE", "Estonia"), ("FI", "Finland"), ("LV", "Latvia"), ("LT", "Lithuania")],
        string="Default Country",
        default="EE",
        help="Default destination country for shipments",
    )
    smartposti_use_door_code = fields.Boolean(
        string="Use Door Code Service",
        default=False,
        help="Enable door code service (requires SmartPosti activation)",
    )
    smartposti_default_place_type = fields.Selection(
        [
            ("apt", "Blue Box"),
            ("ipb", "White Box"),
            ("po", "Post Office"),
            ("pudo", "Parcel Point"),
        ],
        string="Default Place Type",
        default="apt",
        help="Default pickup point type",
    )
    smartposti_default_size = fields.Selection(
        [
            ("XS", "Extra Small"),
            ("S", "Small"),
            ("M", "Medium"),
            ("L", "Large"),
            ("XL", "Extra Large"),
        ],
        string="Default Package Size",
        default="M",
        help="Default package size for shipments",
    )
    smartposti_label_format = fields.Selection(
        [
            ("A4/4", "A4/4"),
            ("A4-4", "A4-4"),
            ("A4/8", "A4/8"),
            ("A4-8", "A4-8"),
            ("A5", "A5"),
            ("A6", "A6"),
            ("A7", "A7"),
        ],
        string="Label Format",
        default="A5",
        help="Default label format for printing",
    )

    # ==================== NEW: PRICE CONFIGURATION ====================
    smartposti_pudo_price = fields.Float(
        string="Parcel Machines Price",
        default=3.50,
        help="Fixed delivery price for parcel machines (PUDO)",
    )
    smartposti_courier_price = fields.Float(
        string="Courier Price",
        default=5.50,
        help="Fixed delivery price for courier (door-to-door)",
    )

    # Additional Services
    smartposti_enable_express = fields.Boolean(
        string="Enable Express Service",
        default=False,
        help="Allow express delivery option",
    )
    smartposti_enable_id_check = fields.Boolean(
        string="Enable ID Check",
        default=False,
        help="Require ID verification on delivery",
    )
    smartposti_enable_age_check = fields.Boolean(
        string="Enable Age Check",
        default=False,
        help="Require age verification on delivery",
    )
    smartposti_enable_cod = fields.Boolean(
        string="Enable Cash on Delivery", default=False, help="Allow COD payment option"
    )
    smartposti_notification_email = fields.Char(
        string="Notification Email", help="Default email for delivery notifications"
    )
    smartposti_notification_phone = fields.Char(
        string="Notification Phone", help="Default phone for delivery notifications"
    )

    # Return Configuration
    smartposti_return_days = fields.Integer(
        string="Return Days",
        default=14,
        help="Days allowed for customer returns (0-90)",
    )
    smartposti_enable_returns = fields.Boolean(
        string="Enable Returns", default=False, help="Allow customer returns"
    )
    smartposti_country_price_ids = fields.One2many(
        "smartposti.country.price", "company_id", string="Country-Based Prices"
    )
    smartposti_custom_service_names = fields.Boolean(
        string="Use Custom Service Names",
        default=False,
        help="Enable custom naming for delivery service types",
    )
    smartposti_courier_label = fields.Char(
        string="Courier Service Label",
        default="Kuller (uksele)",
        help="Custom label for courier delivery service",
    )
    smartposti_pudo_label = fields.Char(
        string="Parcel Machine Label",
        default="Pakiautomaadid",
        help="Custom label for parcel machine service",
    )

    smartposti_courier_sequence = fields.Integer(
        string="Courier Display Sequence",
        default=1,
        help="Display order for Courier service (lower number appears first)"
    )
    smartposti_pudo_sequence = fields.Integer(
        string="Parcel Machine Display Sequence",
        default=2,
        help="Display order for Parcel Machine service (lower number appears first)"
    )

    @api.constrains("smartposti_return_days")
    def _check_smartposti_return_days(self):
        """Validate return days within acceptable range"""
        for company in self:
            if company.smartposti_enable_returns:
                if not (0 <= company.smartposti_return_days <= 90):
                    raise ValidationError(_("Return days must be between 0 and 90"))

    @api.constrains("smartposti_environment")
    def _onchange_smartposti_environment(self):
        """Update base URL based on environment"""
        if self.smartposti_environment == "demo":
            self.smartposti_base_url = (
                "https://gateway.demo.posti.fi/smartpost/api/ext/v1"
            )
        elif self.smartposti_environment == "live":
            self.smartposti_base_url = "https://gateway.posti.fi/smartpost/api/ext/v1"

    def action_test_smartposti_connection(self):
        """Test SmartPosti API credentials"""
        self.ensure_one()

        if not self.smartposti_api_key or not self.smartposti_gateway_secret:
            raise ValidationError(
                _("Please configure SmartPosti API Key and Gateway Secret first.")
            )

        try:
            from .smartposti_client import SmartPostiClient

            client = SmartPostiClient(
                base_url=self.smartposti_base_url,
                api_key=self.smartposti_api_key,
                gateway_secret=self.smartposti_gateway_secret,
            )

            # Test connection by fetching places
            response = client.get_places(self.smartposti_default_country)

            if response.get("error"):
                raise ValidationError(_("Connection failed: %s") % response["error"])

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Connection to SmartPosti API successful!"),
                    "type": "success",
                    "sticky": False,
                },
            }

        except Exception as e:
            raise ValidationError(_("Connection test failed: %s") % str(e))

    def action_sync_smartposti_places(self):
        """Sync SmartPosti places for all countries"""
        self.ensure_one()

        try:
            Place = self.env["smartposti.place"]

            # All available countries
            all_countries = ["EE", "FI", "LV", "LT"]

            # Create a temporary carrier-like object for sync
            class TempCarrier:
                def __init__(self, company):
                    self.company = company

                def _get_smartposti_client(self):
                    from .smartposti_client import SmartPostiClient

                    return SmartPostiClient(
                        base_url=self.company.smartposti_base_url,
                        api_key=self.company.smartposti_api_key,
                        gateway_secret=self.company.smartposti_gateway_secret,
                    )

            temp_carrier = TempCarrier(self)

            # Sync all countries
            total_created = 0
            total_updated = 0
            total_synced = 0
            failed_countries = []

            for country in all_countries:
                try:
                    result = Place.sync_places_for_country(country, temp_carrier)
                    total_created += result["created"]
                    total_updated += result["updated"]
                    total_synced += result["total"]
                except Exception as e:
                    failed_countries.append(f"{country}: {str(e)}")
                    continue

            # Prepare result message
            message_parts = [
                f"Total Created: {total_created}",
                f"Total Updated: {total_updated}",
                f"Total Synced: {total_synced}",
                f"Countries: {', '.join(all_countries)}",
            ]

            if failed_countries:
                message_parts.append(f"\nFailed: {', '.join(failed_countries)}")
                notification_type = "warning"
            else:
                notification_type = "success"

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Places Synced"),
                    "message": "\n".join(message_parts),
                    "type": notification_type,
                    "sticky": True,
                },
            }

        except Exception as e:
            raise ValidationError(_("Sync failed: %s") % str(e))
