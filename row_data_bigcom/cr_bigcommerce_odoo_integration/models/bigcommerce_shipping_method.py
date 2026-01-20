# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import requests
from odoo.exceptions import UserError
from odoo import models, fields, _

class BigCommerceShippingMethod(models.Model):
    _name = 'bigcommerce.shipping.method'
    _description = 'BigCommerce Shipping Method'

    bc_method_id = fields.Integer(string="BC Method ID", required=True, readonly=True)
    name = fields.Char(string="Name", required=True)
    type = fields.Char(string="Type")
    enabled = fields.Boolean(string="Enabled")
    fixed_surcharge = fields.Float(string="Fixed Surcharge")
    is_fallback = fields.Boolean(string="Is Fallback")
    channel_ids_text = fields.Char(string="Channel IDs (CSV)")
    store_id = fields.Many2one('bigcommerce.store', string="BigCommerce Store")
    zone_id = fields.Many2one('bigcommerce.shipping.zone', string="Shipping Zone")
    # New fields based on settings
    minimum_sub_total = fields.Float(string="Minimum Subtotal")
    exclude_fixed_shipping_products = fields.Boolean(string="Exclude Fixed Shipping Products")
    use_discounted_sub_total = fields.Boolean(string="Use Discounted Subtotal")
    rate = fields.Float(string="Rate")

    def action_refresh_shipping_method(self):
        self.ensure_one()

        if not self.store_id or not self.zone_id:
            raise UserError(_("Store and Zone must be set to refresh shipping method."))

        url = f"https://api.bigcommerce.com/stores/{self.store_id.store_hash}/v2/shipping/zones/{self.zone_id.zone_id}/methods/{self.bc_method_id}"
        headers = {
            'X-Auth-Token': self.store_id.access_token,
            'Accept': 'application/json',
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise UserError(_("Failed to fetch shipping method.\nStatus: %s\nResponse: %s") %
                            (response.status_code, response.text))

        method = response.json()

        carrier_options = method.get('settings', {}).get('carrier_options', {})

        self.write({
            'name': method.get('name'),
            'type': method.get('type'),
            'enabled': method.get('enabled', False),
            'fixed_surcharge': float(method.get('handling_fees', {}).get('fixed_surcharge', 0)),
            'is_fallback': method.get('is_fallback', False),
            'minimum_sub_total': float(carrier_options.get('minimum_sub_total', 0)),
            'exclude_fixed_shipping_products': carrier_options.get('exclude_fixed_shipping_products', "0") == "1",
            'use_discounted_sub_total': carrier_options.get('use_discounted_sub_total', "0") == "1",
            'rate': float(method.get('settings', {}).get('rate', 0)),
            'channel_ids_text': ','.join(str(cid) for cid in method.get('channel_ids', [])),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Shipping Method Updated"),
                'message': _("Successfully refreshed shipping method data from BigCommerce."),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_export_shipping_method(self):
        self.ensure_one()

        if not self.store_id or not self.zone_id:
            raise UserError(_("Store and Zone must be set to export shipping method."))

        # Prepare settings based on type
        settings = {}
        if self.type == 'perorder' or self.type == 'peritem':
            settings = {'rate': self.rate}
        elif self.type == 'freeshipping':
            settings = {
                'carrier_options': {
                    'minimum_sub_total': str(self.minimum_sub_total),
                    'exclude_fixed_shipping_products': "1" if self.exclude_fixed_shipping_products else "0",
                    'use_discounted_sub_total': "1" if self.use_discounted_sub_total else "0",
                    'packaging': []
                }
            }
        # You can add logic here for other types: `weight`, `total`, etc.

        # Prepare payload
        payload = {
            'name': self.name,
            'type': self.type,
            'settings': settings,
            'enabled': self.enabled,
            'handling_fees': {
                'fixed_surcharge': str(self.fixed_surcharge)
            },
        }

        # Include channel_ids if present
        if self.channel_ids_text:
            try:
                channel_ids = [int(cid.strip()) for cid in self.channel_ids_text.split(',') if cid.strip().isdigit()]
                payload['channel_ids'] = channel_ids
            except ValueError:
                raise UserError(_("Invalid Channel IDs format."))

        url = f"https://api.bigcommerce.com/stores/{self.store_id.store_hash}/v2/shipping/zones/{self.zone_id.zone_id}/methods/{self.bc_method_id}"
        headers = {
            'X-Auth-Token': self.store_id.access_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        response = requests.put(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise UserError(_("Failed to export shipping method.\nStatus: %s\nResponse: %s") %
                            (response.status_code, response.text))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Shipping Method Updated"),
                'message': _("Successfully exported shipping method to BigCommerce."),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_delete_shipping_method(self):
        self.ensure_one()

        if not self.store_id or not self.zone_id or not self.bc_method_id:
            raise UserError(_("Store, Zone, and Method ID must be set to delete shipping method."))

        url = f"https://api.bigcommerce.com/stores/{self.store_id.store_hash}/v2/shipping/zones/{self.zone_id.zone_id}/methods/{self.bc_method_id}"
        headers = {
            'X-Auth-Token': self.store_id.access_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        response = requests.delete(url, headers=headers)

        if response.status_code not in [200, 204]:
            raise UserError(_("Failed to delete shipping method.\nStatus: %s\nResponse: %s") %
                            (response.status_code, response.text))

        # Optional: delete the record from Odoo
        self.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Shipping Method Deleted"),
                'message': _("Shipping method successfully deleted from BigCommerce and Odoo."),
                'type': 'success',
                'sticky': False,
            }
        }