# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from itertools import count

from odoo import models, fields
import requests
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    bigcommerce_product_attribute_id = fields.Integer("BigCommerce Product Attribute ID")
    bigcommerce_product_id = fields.Integer("BigCommerce Product ID")
    bigcommerce_sku = fields.Char("BigCommerce SKU")
    bigcommerce_sku_id = fields.Integer("BigCommerce SKU ID")
    bigcommerce_store_id = fields.Many2one('bigcommerce.store', string="BigCommerce Store")

    def action_export_inventory_to_bigcommerce(self, store):
        """
        Export inventory for selected products to BigCommerce using absolute adjustment.
        :param store: A record of `bigcommerce.store` with store_hash and access_token
        """
        count = 0
        if not store or not store.store_hash or not store.access_token:
            raise ValueError("Store configuration is missing or invalid.")

        # Prepare the inventory payload
        inventory_items = []
        reason = "Inventory sync from Odoo"

        for product in self:
            if not product.default_code and not product.bigcommerce_variant_id:
                _logger.warning("Skipping product %s — missing SKU or BigCommerce Variant ID.", product.name)
                continue

            # Get stock quantity (you may adapt this logic per your business rules)
            quantity = sum(product.stock_quant_ids.mapped('quantity'))  # Adjust if needed
            location_id = product.stock_quant_ids[:1].location_id.bc_location_id  # Custom field needed

            if not location_id:
                _logger.warning("No BigCommerce location ID mapped for product %s", product.name)
                continue

            item_data = {
                "location_id": location_id,
                "quantity": int(quantity)
            }

            # Choose identifier
            if product.bigcommerce_product_attribute_id:
                item_data["variant_id"] = product.bigcommerce_product_attribute_id
            elif product.default_code:
                item_data["sku"] = product.default_code
            count += 1
            inventory_items.append(item_data)

        if not inventory_items:
            _logger.info("No inventory updates to export.")
            return

        payload = {
            "reason": reason,
            "items": inventory_items
        }

        # API Call
        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/adjustments/absolute"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            transaction_id = data.get("transaction_id")
            _logger.info("Inventory exported. Transaction ID: %s", transaction_id)
        except requests.exceptions.RequestException as e:
            _logger.error("Error exporting inventory: %s", e)
            raise

        return count

    def action_update_variant(self):
        """Update product variant data from BigCommerce API."""
        self.ensure_one()
        store = self.bigcommerce_store_id
        if not store or not store.access_token or not store.store_hash:
            raise UserError("BigCommerce store configuration is missing or incomplete.")

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{self.bigcommerce_product_id}/variants/{self.bigcommerce_product_attribute_id}"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Auth-Token': store.access_token
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get('data', {})

            # Update fields based on API response
            update_vals = {
                'bigcommerce_sku': data.get('sku'),
                'bigcommerce_sku_id': data.get('sku_id'),
                'list_price': data.get('price', 0.0),
                'standard_price': data.get('cost_price', 0.0),
                'weight': data.get('weight', 0.0),
                'bigcommerce_width': data.get('width', 0.0),
                'bigcommerce_height': data.get('height', 0.0),
                'bigcommerce_depth': data.get('depth', 0.0),
                'bigcommerce_sale_price': data.get('sale_price', 0.0),
                'bigcommerce_map_price': data.get('map_price', 0.0),
                'bigcommerce_calculated_price': data.get('calculated_price', 0.0),
                'bigcommerce_upc': data.get('upc', ''),
                'bigcommerce_mpn': data.get('mpn', ''),
                'bigcommerce_gtin': data.get('gtin', ''),
                'bigcommerce_inventory_level': data.get('inventory_level', 0),
            }

            self.write(update_vals)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Product variant updated successfully.',
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.RequestException as e:
            raise UserError(f"Failed to update variant: {str(e)}")

    # def action_update_bigcommerce_variant(self):
    #     for variant in self:
    #         store = variant.product_tmpl_id.bigcommerce_store_id
    #         # if not store or not variant.bigcommerce_product_id or not variant.bigcommerce_variant_id:
    #         #     raise UserError("Missing store, product ID, or variant ID.")
    #
    #         url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{variant.bigcommerce_product_id}/variants/{variant.bigcommerce_variant_id}"
    #         headers = {
    #             'X-Auth-Token': store.access_token,
    #             'Content-Type': 'application/json',
    #             'Accept': 'application/json'
    #         }
    #
    #         payload = {
    #             "sku": variant.default_code or "",
    #             "price": variant.lst_price or 0.0,
    #             "cost_price": variant.standard_price or 0.0,
    #             "inventory_level": int(variant.qty_available),
    #             "weight": variant.weight or 0.0,
    #             "sale_price": variant.lst_price or 0.0,
    #             "retail_price": variant.lst_price or 0.0,
    #             "is_free_shipping": False,
    #             "fixed_cost_shipping_price": 0.0,
    #             "inventory_warning_level": 5,
    #             "bin_picking_number": "",
    #             "mpn": "",
    #             "gtin": ""
    #         }
    #
    #         response = requests.put(url, headers=headers, json=payload)
    #         if response.status_code != 200:
    #             raise UserError(f"Failed to update variant in BigCommerce:\n{response.status_code} - {response.text}")
