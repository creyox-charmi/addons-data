# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields
import requests
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    bigcommerce_product_attribute_id = fields.Integer(
        "BigCommerce Product Attribute ID"
    )
    bigcommerce_product_id = fields.Integer("BigCommerce Product ID")
    bigcommerce_sku = fields.Char("BigCommerce SKU")
    bigcommerce_sku_id = fields.Integer("BigCommerce SKU ID")
    bigcommerce_store_id = fields.Many2one(
        "bigcommerce.store", string="BigCommerce Store"
    )

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

        data = self.env["product.product"].search(
            [("bigcommerce_store_id", "=", store.id)]
        )

        for product in data:
            if (
                not product.default_code
                and not product.bigcommerce_product_attribute_id
            ):
                _logger.warning(
                    "Skipping product %s — missing SKU or BigCommerce Variant ID.",
                    product.name,
                )
                continue

            valid_quants = product.stock_quant_ids.filtered(
                lambda q: q.location_id.usage == "internal"
                and q.location_id.bc_location_id
            )

            quantity = sum(valid_quants.mapped("quantity"))

            if not valid_quants or quantity <= 0:
                _logger.warning(
                    "No valid stock quant or zero quantity for product %s", product.name
                )
                continue

            location_id = valid_quants[0].location_id.bc_location_id

            item_data = {"location_id": int(location_id), "quantity": int(quantity)}

            if product.bigcommerce_product_attribute_id:
                item_data["variant_id"] = product.bigcommerce_product_attribute_id
            elif product.default_code:
                item_data["sku"] = product.default_code

            inventory_items.append(item_data)
            count += 1

        if not inventory_items:
            _logger.info("No inventory updates to export.")
            return

        payload = {"reason": reason, "items": inventory_items}

        print("payload : ", payload)
        # API Call
        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/adjustments/absolute"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
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
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": store.access_token,
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get("data", {})

            # Update fields based on API response
            update_vals = {
                "bigcommerce_sku": data.get("sku"),
                "bigcommerce_sku_id": data.get("sku_id"),
                "list_price": data.get("price", 0.0),
                "standard_price": data.get("cost_price", 0.0),
                "weight": data.get("weight", 0.0),
                "bigcommerce_width": data.get("width", 0.0),
                "bigcommerce_height": data.get("height", 0.0),
                "bigcommerce_depth": data.get("depth", 0.0),
                "bigcommerce_sale_price": data.get("sale_price", 0.0),
                "bigcommerce_map_price": data.get("map_price", 0.0),
                "bigcommerce_calculated_price": data.get("calculated_price", 0.0),
                "bigcommerce_upc": data.get("upc", ""),
                "bigcommerce_mpn": data.get("mpn", ""),
                "bigcommerce_gtin": data.get("gtin", ""),
                "bigcommerce_inventory_level": data.get("inventory_level", 0),
            }

            self.write(update_vals)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Product variant updated successfully.",
                    "type": "success",
                    "sticky": False,
                },
            }

        except requests.exceptions.RequestException as e:
            raise UserError(f"Failed to update variant: {str(e)}")
