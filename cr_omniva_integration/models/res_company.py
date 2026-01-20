# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    # Omniva API Configuration (existing fields...)
    omniva_api_url = fields.Selection(
        [("test", "Test Environment"), ("live", "Live Environment")],
        string="Omniva Environment",
        default="test",
    )

    omniva_username = fields.Char(string="Omniva Username")
    omniva_password = fields.Char(string="Omniva Password")
    omniva_customer_code = fields.Char(
        string="Customer Code", help="Your Omniva customer code (e.g., 37884)"
    )
    omniva_developer_id = fields.Char(
        string="Developer ID",
        default="Developer_ODOO18_v1",
        help="X-Integration-Agent-Id header value",
    )
    omniva_default_hs_code = fields.Char(
        string="Default Omniva HS Code",
        size=10,
        help="Default 10-digit HS code for non-EU customs",
    )

    # ==================== NEW: PRICE CONFIGURATION ====================
    omniva_courier_price = fields.Float(
        string="Courier Delivery Price",
        default=5.00,
        help="Fixed delivery price for door-to-door courier delivery",
    )
    omniva_parcel_machine_price = fields.Float(
        string="Parcel Machine Price",
        default=3.50,
        help="Fixed delivery price for parcel machine pickup",
    )
    omniva_post_office_price = fields.Float(
        string="Post Office Price",
        default=4.00,
        help="Fixed delivery price for post office pickup",
    )
    omniva_country_price_ids = fields.One2many(
        "omniva.country.price", "company_id", string="Country-Based Prices"
    )
    omniva_custom_service_names = fields.Boolean(
        string="Use Custom Service Names",
        default=False,
        help="Enable custom naming for delivery service types",
    )
    omniva_courier_label = fields.Char(
        string="Courier Service Label",
        default="Kuller (uksele)",
        help="Custom label for courier delivery service",
    )
    omniva_pudo_label = fields.Char(
        string="Parcel Machine Label",
        default="Pakiautomaadid",
        help="Custom label for parcel machine service",
    )
    omniva_post_office_label = fields.Char(
        string="Post office Label",
        default="Postkontor",
        help="Custom label for Post office service",
    )
    # Add these fields to ResCompany model

    omniva_courier_sequence = fields.Integer(
        string="Courier Display Sequence",
        default=1,
    )
    omniva_parcel_machine_sequence = fields.Integer(
        string="Parcel Machine Display Sequence",
        default=2,
    )
    omniva_post_office_sequence = fields.Integer(
        string="Post Office Display Sequence",
        default=3,
    )

    @api.constrains("omniva_courier_sequence", "omniva_parcel_machine_sequence", "omniva_post_office_sequence")
    def _check_omniva_service_sequences(self):
        for company in self:
            if company.omniva_courier_sequence < 1:
                raise ValidationError(_("Courier sequence must be greater than 0"))
            if company.omniva_parcel_machine_sequence < 1:
                raise ValidationError(_("Parcel Machine sequence must be greater than 0"))
            if company.omniva_post_office_sequence < 1:
                raise ValidationError(_("Post Office sequence must be greater than 0"))
    # ==================================================================

    def _get_omniva_base_url(self):
        """Get the base URL based on environment selection."""
        self.ensure_one()
        if self.omniva_api_url == "live":
            return "https://omx.omniva.eu/api/v01/omx"
        return "https://test-omx.omniva.eu/api/v01/omx"

    def action_test_omniva_connection(self):
        """Test Omniva API credentials"""
        self.ensure_one()

        if not self.omniva_username or not self.omniva_password:
            raise ValidationError(
                _("Please configure Omniva username and password first.")
            )

        if not self.omniva_customer_code:
            raise ValidationError(_("Please configure Omniva customer code first."))

        import requests
        import base64

        base_url = self._get_omniva_base_url()
        credentials = f"{self.omniva_username}:{self.omniva_password}"
        auth_token = base64.b64encode(credentials.encode("utf-8")).decode("ascii")

        headers = {
            "Authorization": f"Basic {auth_token}",
            "X-Integration-Agent-Id": self.omniva_developer_id or "Developer_ODOO18_v1",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(
                f"{base_url}/shipments",
                headers=headers,
                params={"fromTrackEventId": 0, "size": 1},
                timeout=10,
            )

            if response.status_code == 200:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Success"),
                        "message": _("Connection to Omniva API successful!"),
                        "type": "success",
                        "sticky": False,
                    },
                }
            elif response.status_code == 401:
                raise ValidationError(
                    _("Authentication failed. Please verify credentials.")
                )
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", response.text)
                except:
                    error_msg = response.text

                raise ValidationError(
                    _("Connection failed with status %s: %s")
                    % (response.status_code, error_msg)
                )

        except ValidationError:
            raise
        except requests.RequestException as e:
            raise ValidationError(_("Network error: %s") % str(e))
        except Exception as e:
            raise ValidationError(_("Unexpected error: %s") % str(e))

    def action_sync_omniva_locations(self):
        """Sync Omniva locations"""
        self.ensure_one()

        try:
            Location = self.env["omniva.location"]
            result = Location.sync_locations_from_omniva()

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Locations Synced"),
                    "message": _(
                        "Created: %(created)s, Updated: %(updated)s, Total: %(total)s"
                    )
                    % result,
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            raise ValidationError(_("Sync failed: %s") % str(e))
