# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class BigCommerceShippingZone(models.Model):
    _name = 'bigcommerce.shipping.zone'
    _description = 'BigCommerce Shipping Zone'
    _rec_name = 'name'

    bigcommerce_store_id = fields.Many2one(
        'bigcommerce.store',
        string="BigCommerce Store",
        required=True,
        ondelete='cascade',
        help="The store this shipping zone belongs to."
    )
    name = fields.Char(string="Zone Name", required=True)
    zone_id = fields.Integer(string="BigCommerce Zone ID", required=True, readonly=True)
    type = fields.Selection([
        ('country', 'Country'),
        ('state', 'State'),
        ('zip', 'Zip'),
        ('address', 'Address'),
    ], string="Type")
    country_iso2 = fields.Char(string="Country ISO Code")

    free_shipping_enabled = fields.Boolean(string="Free Shipping Enabled")
    free_shipping_minimum_sub_total = fields.Float(string="Free Shipping Min Subtotal")
    exclude_fixed_shipping_products = fields.Boolean(string="Exclude Fixed Shipping Products")

    display_separately = fields.Boolean(string="Display Handling Fees Separately")
    fixed_surcharge = fields.Float(string="Handling Fee Surcharge")
    enabled = fields.Boolean(string="Enabled")

    location_id = fields.Many2one('bigcommerce.inventory.location', string="Location")
    shipping_method_ids = fields.One2many(
        'bigcommerce.shipping.method',
        'zone_id',
        string="Shipping Methods"
    )

    def update_zone_from_bigcommerce(self):
        for record in self:
            store = record.bigcommerce_store_id
            if not store or not store.access_token or not store.store_hash:
                raise UserError(_("Missing API credentials in store."))

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/shipping/zones/{record.zone_id}"
            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise UserError(_("Failed to fetch shipping zone. Response: %s") % response.text)

            data = response.json()

            record.write({
                'name': data.get('name'),
                'type': data.get('type'),
                'free_shipping_enabled': data.get('free_shipping', {}).get('enabled'),
                'free_shipping_minimum_sub_total': float(data.get('free_shipping', {}).get('minimum_sub_total', 0.0)),
                'exclude_fixed_shipping_products': data.get('free_shipping', {}).get('exclude_fixed_shipping_products'),
                'display_separately': data.get('handling_fees', {}).get('display_separately'),
                'fixed_surcharge': float(data.get('handling_fees', {}).get('fixed_surcharge', 0.0)),
                'enabled': data.get('enabled'),
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Zone Updated"),
                    'message': _("Successfully updated the shipping zone '%s'.") % record.name,
                    'type': 'success',
                    'sticky': False,
                }
            }
        return None

    def export_zone_to_bigcommerce(self):
        for record in self:
            store = record.bigcommerce_store_id
            if not store or not store.access_token or not store.store_hash:
                raise UserError(_("Missing API credentials in store."))

            if not record.name:
                raise UserError(_("Zone name is required."))

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/shipping/zones/{record.zone_id}"
            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            payload = {
                "name": record.name,
                "type": record.type,
                "enabled": record.enabled,
                "locations": [{"id": int(record.location_id.bc_location_id),"country_iso2":record.country_iso2}],
                "free_shipping": {
                    "enabled": record.free_shipping_enabled,
                    "minimum_sub_total": f"{record.free_shipping_minimum_sub_total:.4f}",
                    "exclude_fixed_shipping_products": record.exclude_fixed_shipping_products
                },
                "handling_fees": {
                    "fixed_surcharge": f"{record.fixed_surcharge:.4f}",
                    "display_separately": record.display_separately
                }
            }

            response = requests.put(url, headers=headers, json=payload)

            if response.status_code != 200:
                raise UserError(_("Failed to update zone in BigCommerce. Response: %s") % response.text)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Shipping Zone Updated"),
                    'message': _("Zone '%s' successfully updated in BigCommerce.") % record.name,
                    'type': 'success',
                    'sticky': False,
                }
            }
        return None

    def delete_zone_from_bigcommerce(self):
        for record in self:
            store = record.bigcommerce_store_id
            if not store or not store.store_hash or not store.access_token:
                raise UserError(_("Store information is missing or incomplete."))

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/shipping/zones/{record.bc_zone_id}"
            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                # Optionally unlink from Odoo too
                record.unlink()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Delete Successful"),
                        'message': _("Shipping Zone deleted successfully from BigCommerce and Odoo."),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("Failed to delete shipping zone. Response: %s") % response.text)
        return None

    def action_bulk_update_zone_from_bigcommerce(self):
        for record in self:
            try:
                record.update_zone_from_bigcommerce()
            except Exception as e:
                _logger.exception("Zone update failed for %s: %s", record.name, str(e))

    def action_bulk_export_zone_to_bigcommerce(self):
        for record in self:
            try:
                record.export_zone_to_bigcommerce()
            except Exception as e:
                _logger.exception("Zone export failed for %s: %s", record.name, str(e))


