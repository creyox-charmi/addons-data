# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

VALID_US_STATE_CODES = [
    'AL', 'AK', 'AS', 'AZ', 'AR', 'AE', 'AA', 'AP', 'CA', 'CO', 'CT', 'DE', 'DC', 'FM', 'FL', 'GA', 'GU',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MH', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT',
    'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY'
]

class BigCommerceInventoryLocation(models.Model):
    _name = 'bigcommerce.inventory.location'
    _description = 'BigCommerce Inventory Location'
    _rec_name = 'label'

    bigcommerce_store_id = fields.Many2one(
        'bigcommerce.store',
        string="BigCommerce Store",
        help="The store this inventory location belongs to."
    )
    bc_location_id = fields.Char(string="BC Location ID", required=True, readonly=True)
    code = fields.Char(string="Code", required=True)
    label = fields.Char(string="Label", required=True)
    description = fields.Text(string="Description")
    managed_by_external_source = fields.Boolean(string="Managed Externally")
    type_id = fields.Selection([('PHYSICAL', 'Physical'), ('VIRTUAL', 'Virtual')], string="Type")
    enabled = fields.Boolean(string="Enabled")
    operating_hours = fields.Text(string="Operating Hours")
    time_zone = fields.Char(string="Time Zone")
    created_at = fields.Datetime(string="Created At")
    updated_at = fields.Datetime(string="Updated At")

    # Address fields
    address1 = fields.Char(string="Address 1")
    address2 = fields.Char(string="Address 2")
    city = fields.Char(string="City")
    state = fields.Char(string="State")
    zip = fields.Char(string="Zip Code")
    phone = fields.Char(string="Phone")
    country_code = fields.Char(string="Country Code")
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")

    storefront_visibility = fields.Boolean(string="Visible on Storefront")

    def action_update_location_to_bigcommerce(self):
        for rec in self:
            store = rec.bigcommerce_store_id
            if not store:
                raise UserError(_("No BigCommerce Store is set on this location."))

            if not rec.bc_location_id:
                raise UserError(_("No BigCommerce Location ID found for update."))

            api_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations"

            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            payload = [{
                "id": int(rec.bc_location_id),
                "code": rec.code,
                "label": rec.label,
                "description": rec.description or "",
                "managed_by_external_source": rec.managed_by_external_source,
                "type_id": rec.type_id or "PHYSICAL",
                "enabled": rec.enabled,
                "operating_hours": None,
                "time_zone": rec.time_zone or "Etc/UTC",
                "address": {
                    "address1": rec.address1 or "N/A",
                    "email": store.admin_email or "no-reply@example.com",
                    "address2": rec.address2 or "",
                    "city": rec.city or "N/A",
                    "state": rec.state if rec.state else "CA",
                    "zip": rec.zip or "00000",
                    "phone": rec.phone or "",
                    "geo_coordinates": {
                        "latitude": rec.latitude,
                        "longitude": rec.longitude
                    },
                    "country_code": rec.country_code or "US"
                },
                "storefront_visibility": rec.storefront_visibility,
                "special_hours": []
            }]
            print('payload :' ,payload)
            response = requests.put(api_url, headers=headers, json=payload)

            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Update Complete"),
                        'message': _("Location updated successfully to BigCommerce."),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                _logger.error("Failed to update location: %s", response.text)
                raise UserError(_("Failed to update location. Response: %s") % response.text)
        return None

    def action_delete_location_from_bigcommerce(self):
        for rec in self:
            store = rec.bigcommerce_store_id

            if not store:
                raise UserError(_("BigCommerce Store is not set on this location."))

            if not rec.bc_location_id:
                raise UserError(_("No BigCommerce Location ID found to delete."))

            if rec.bc_location_id == 1:
                raise UserError(_("Location ID 1 is the default shipping origin and cannot be deleted."))

            api_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations"
            print('api_url : ',api_url)
            params = {
                "location_id:in": int(self.bc_location_id)
            }
            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
            }

            response = requests.delete(api_url, headers=headers,params=params)

            if response.status_code == 200:
                rec.unlink()  # Optionally remove the record from Odoo too
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Delete Successful"),
                        'message': _("The location was successfully deleted from BigCommerce."),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                _logger.error("Failed to delete location: %s", response.text)
                raise UserError(_("Failed to delete location. Response: %s") % response.text)
        return None

