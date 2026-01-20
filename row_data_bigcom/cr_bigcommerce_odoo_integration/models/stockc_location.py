# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from datetime import datetime

import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class StockLocation(models.Model):
    _inherit = 'stock.location'

    bigcommerce_store_id = fields.Many2one(
        'bigcommerce.store',
        string="BigCommerce Store",
        help="The store this inventory location belongs to."
    )
    bc_location_id = fields.Char(string="BC Location ID", readonly=True)
    code = fields.Char(string="Location Code")  # stock.location already has 'name', so 'code' is custom here
    label = fields.Char(string="Label")
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
    transaction_id = fields.Char(string='transaction_id')

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

    def action_bulk_update_locations_to_bigcommerce(self):
        if not self:
            return

        store = self[0].bigcommerce_store_id
        if not store or not store.access_token or not store.store_hash:
            raise UserError("Missing store credentials.")

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = []
        for loc in self:
            payload.append({
                "id": int(loc.bc_location_id),
                "code": loc.code,
                "label": loc.label,
                "description": loc.name,
                "managed_by_external_source": loc.managed_by_external_source,
                "type_id": loc.type_id or "PHYSICAL",
                "enabled": loc.enabled,
                "operating_hours": loc.operating_hours or {},
                "time_zone": loc.time_zone or "Etc/UTC",
                "address": {
                    "address1": loc.address1 or "",
                    "address2": loc.address2 or "",
                    "city": loc.city or "",
                    "state": loc.state or "CA",
                    "zip": loc.zip or "000000",
                    "phone": loc.phone or "",
                    "geo_coordinates": {
                        "latitude": loc.latitude or 0,
                        "longitude": loc.longitude or 0
                    },
                    "country_code": loc.country_code or "US"
                },
                "storefront_visibility": loc.storefront_visibility,
                "special_hours": []
            })

        response = requests.put(url, headers=headers, json=payload)
        if response.status_code not in [200, 207]:
            raise UserError(f"Bulk update failed: {response.text}")

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _("Locations Updated"),
        #         'message': _("All selected locations have been updated on BigCommerce."),
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }

    def action_sync_inventory(self):
        print('YES CALLLL')
        """Sync BigCommerce inventory to Odoo stock.quant."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cr.select.store',
            'view_mode': 'form',
            'target': 'new',
            'views': [(False, 'form')],
            'context': {'default_location_ids': self.env.context.get('active_ids', self.ids)},
        }
        # self.ensure_one()
        # # Initialize timestamp for logging
        # initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #
        # try:
        #     headers = {
        #         "X-Auth-Token": self.access_token,
        #         "Accept": "application/json",
        #         "Content-Type": "application/json"
        #     }
        #     url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/inventory/items"
        #     # Fetch first page
        #     response = requests.get(url, headers=headers, params={'limit': 1000, 'page': 1})
        #     response.raise_for_status()
        #     data = response.json()
        #     items = data['data']
        #     pagination = data['meta']['pagination']
        #     total_pages = pagination['total_pages']
        #
        #     # Handle pagination
        #     for page in range(2, total_pages + 1):
        #         response = requests.get(url, headers=headers, params={'limit': 1000, 'page': page})
        #         response.raise_for_status()
        #         items.extend(response.json()['data'])
        #
        #     self.env['cr.data.processing.log']._log_data_processing(
        #         cr_shop_id=self.id,
        #         record_count=1,
        #         cr_message=f"Fetched {len(items)} inventory items across {total_pages} pages for store {self.store_hash}",
        #         status='success',
        #         timespan=str(fields.Datetime.now()),
        #         initiated_at=str(fields.Datetime.now()),
        #         error_message='',
        #         cr_user_id=self.env.uid
        #     )
        #
        # except requests.exceptions.RequestException as e:
        #     error_msg = f"Failed to fetch inventory for store {self.store_hash}: {str(e)}"
        #     _logger.error(error_msg)
        #     self.env['cr.data.processing.log']._log_data_processing(
        #         cr_shop_id=self.id,
        #         record_count=1,
        #         cr_message="Failed to fetch inventory items",
        #         status='failure',
        #         timespan=str(fields.Datetime.now()),
        #         initiated_at=str(fields.Datetime.now()),
        #         error_message=error_msg,
        #         cr_user_id=self.env.uid
        #     )
        #     raise UserError(_("Failed to fetch inventory: %s") % str(e))
        #
        # skipped_items = []
        # created_quants = 0
        # updated_quants = 0
        # try:
        #     for item in items:
        #         identity = item['identity']
        #         product = self.env['product.product'].sudo().search([
        #             ('bigcommerce_product_id', '=', identity['product_id']),
        #             ('bigcommerce_product_attribute_id', '=', str(identity['variant_id'])),
        #         ], limit=1)
        #
        #         if not product:
        #             product1 = self.env['product.product'].sudo().search([
        #                 ('bigcommerce_product_id', '=', identity['product_id']),
        #             ], limit=1)
        #             product = product1
        #             if not product1:
        #                 _logger.warning("No product found for product_id %s, variant_id %s (store %s), SKU %s",
        #                                 identity['product_id'], identity['variant_id'], self.store_hash,
        #                                 identity['sku'])
        #                 self.env['cr.data.processing.log']._log_data_processing(
        #                     cr_shop_id=self.id,
        #                     record_count=1,
        #                     cr_message=f"Skipped product for SKU {identity['sku']}: No product found (store {self.store_hash})",
        #                     status='success',
        #                     timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        #                     initiated_at=initiated_at,
        #                     error_message=f"No product found for product_id {identity['product_id']}, variant_id {identity['variant_id']}",
        #                     cr_user_id=self.env.uid
        #                 )
        #                 skipped_items.append(identity['sku'])
        #                 continue
        #
        #         for location in item['locations']:
        #             if not (location['location_enabled'] and location['settings']['is_in_stock']):
        #                 _logger.info("Skipping disabled or out-of-stock location %s for SKU %s (store %s)",
        #                              location['location_id'], identity['sku'], self.store_hash)
        #                 self.env['cr.data.processing.log']._log_data_processing(
        #                     cr_shop_id=self.id,
        #                     record_count=1,
        #                     cr_message=f"Skipped location {location['location_id']} for SKU {identity['sku']}: Disabled or out-of-stock (store {self.store_hash})",
        #                     status='success',
        #                     timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        #                     initiated_at=initiated_at,
        #                     error_message=f"Location {location['location_code']} disabled or out-of-stock",
        #                     cr_user_id=self.env.uid
        #                 )
        #                 continue
        #
        #             stock_location = self.env['stock.location'].sudo().search([
        #                 ('bc_location_id', '=', str(location['location_id'])),
        #                 ('bigcommerce_store_id', '=', self.id)
        #             ], limit=1)
        #
        #             if not stock_location:
        #                 _logger.warning("No stock location found for location_id %s (store %s), SKU %s",
        #                                 location['location_id'], self.store_hash, identity['sku'])
        #                 self.env['cr.data.processing.log']._log_data_processing(
        #                     cr_shop_id=self.id,
        #                     record_count=1,
        #                     cr_message=f"Skipped stock for SKU {identity['sku']} at location {location['location_code']}: No stock location found (store {self.store_hash})",
        #                     status='success',
        #                     timespan=str(fields.Datetime.now()),
        #                     initiated_at=str(fields.Datetime.now()),
        #                     error_message=f"No stock location found for location_id {location['location_id']}",
        #                     cr_user_id=self.env.uid
        #                 )
        #                 skipped_items.append(f"{identity['sku']} at location {location['location_code']}")
        #                 continue
        #
        #             # # Update low stock threshold
        #             # product.write({
        #             #     'low_stock_threshold': location['settings']['warning_level']
        #             # })
        #
        #             # Update stock.quant
        #             quant = self.env['stock.quant'].sudo().search([
        #                 ('product_id', '=', product.id),
        #                 ('location_id', '=', stock_location.id)
        #             ], limit=1)
        #
        #             quantity = location['available_to_sell'] - location['settings']['safety_stock']
        #             if quantity < 0:
        #                 quantity = 0
        #
        #             if quant:
        #                 quant.with_context(inventory_mode=True).write({
        #                     'quantity': quantity,
        #                     'inventory_date': fields.Datetime.now()
        #                 })
        #                 _logger.info("Updated stock for SKU %s at location %s: %s units (store %s)",
        #                              identity['sku'], location['location_code'], quantity, self.store_hash)
        #                 self.env['cr.data.processing.log']._log_data_processing(
        #                     cr_shop_id=self.id,
        #                     record_count=1,
        #                     cr_message=f"Updated stock for SKU {identity['sku']} at location {location['location_code']}: {quantity} units (store {self.store_hash})",
        #                     status='success',
        #                     timespan=str(fields.Datetime.now()),
        #                     initiated_at=str(fields.Datetime.now()),
        #                     error_message='',
        #                     cr_user_id=self.env.uid
        #                 )
        #                 updated_quants += 1
        #             else:
        #                 self.env['stock.quant'].with_context(inventory_mode=True).create({
        #                     'product_id': product.id,
        #                     'location_id': stock_location.id,
        #                     'quantity': quantity,
        #                     'inventory_date': fields.Datetime.now()
        #                 })
        #                 _logger.info("Created stock for SKU %s at location %s: %s units (store %s)",
        #                              identity['sku'], location['location_code'], quantity, self.store_hash)
        #                 self.env['cr.data.processing.log']._log_data_processing(
        #                     cr_shop_id=self.id,
        #                     record_count=1,
        #                     cr_message=f"Created stock for SKU {identity['sku']} at location {location['location_code']}: {quantity} units (store {self.store_hash})",
        #                     status='success',
        #                     timespan=str(fields.Datetime.now()),
        #                     initiated_at=str(fields.Datetime.now()),
        #                     error_message='',
        #                     cr_user_id=self.env.uid
        #                 )
        #                 created_quants += 1
        #
        #     # Prepare notification message
        #     message = _("Inventory synced successfully for store %s.") % self.store_hash
        #     if skipped_items:
        #         message += _(" Skipped items/locations: %s.") % ", ".join(skipped_items)
        #
        #     _logger.info(message)
        #     self.env['cr.data.processing.log']._log_data_processing(
        #         cr_shop_id=self.id,
        #         record_count=1,
        #         cr_message=f"Completed inventory synchronization for store {self.store_hash}: processed {len(items)} items, created {created_quants} stock entries, updated {updated_quants} stock entries, skipped {len(skipped_items)} items/locations",
        #         status='success',
        #         timespan=str(fields.Datetime.now()),
        #         initiated_at=str(fields.Datetime.now()),
        #         error_message='' if not skipped_items else f"Skipped items/locations: {', '.join(skipped_items)}",
        #         cr_user_id=self.env.uid
        #     )
        #
        #     return {
        #         'type': 'ir.actions.client',
        #         'tag': 'display_notification',
        #         'params': {
        #             'title': _('Success'),
        #             'message': message,
        #             'type': 'success',
        #             'sticky': False,
        #         }
        #     }
        #
        # except Exception as e:
        #     error_msg = f"Error syncing inventory for store {self.store_hash}: {str(e)}"
        #     _logger.error(error_msg)
        #     self.env['cr.data.processing.log']._log_data_processing(
        #         cr_shop_id=self.id,
        #         record_count=1,
        #         cr_message="Error syncing inventory",
        #         status='failure',
        #         timespan=str(fields.Datetime.now()),
        #         initiated_at=str(fields.Datetime.now()),
        #         error_message=error_msg,
        #         cr_user_id=self.env.uid
        #     )
        #     raise UserError(_("Error syncing inventory: %s") % str(e))

    def action_export_to_bigcommerce(self, store):
        """
        Exports selected Odoo locations to BigCommerce
        :param store: record of 'bigcommerce.store' containing access_token and store_hash
        """
        for location in self:
            payload = [{
                "code": location.name.replace(" ", "_").upper(),  # Unique identifier
                "label": location.complete_name,
                "description": location.comment or location.name,
                "managed_by_external_source": False,
                "type_id": "PHYSICAL",  # or "VIRTUAL" depending on use case
                "enabled": True,
                "time_zone": "Etc/UTC",
                "address": {
                  "address1": location.company_id.street or "5th Ave",
                  "city": location.company_id.city or "New York",
                  "state": location.company_id.state_id.code or "NY",
                  "zip": location.company_id.zip or "10021",
                  "email": location.company_id.email or "test@example.com",
                  "phone": location.company_id.phone or "800-555-0198",
                  "geo_coordinates": {
                    "latitude": 40.774378,
                    "longitude": -73.9653178
                  },
                  "country_code": location.company_id.country_id.code or "US"
                },
                "storefront_visibility": True,
            }]

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations"
            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                response_data = response.json()
                transaction_id = response_data.get('transaction_id')
                location.write({'transaction_id':transaction_id,'bigcommerce_store_id':store.id})
                print('location : ',location ,' ',location.transaction_id , ' ',location.bigcommerce_store_id)

                print('response.json() : ',response.json())
                _logger.info("Location %s exported to BigCommerce successfully.", location.name)
            except requests.exceptions.HTTPError as errh:
                _logger.error("HTTPError exporting location %s: %s and %s", location.name, str(errh),response.json())
            except Exception as e:
                _logger.error("Unexpected error exporting location %s: %s and %s", location.name, str(e),response.json())

