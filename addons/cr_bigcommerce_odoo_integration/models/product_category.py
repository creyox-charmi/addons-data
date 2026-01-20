# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = "product.category"

    bigcommerce_store_id = fields.Many2one(
        "bigcommerce.store", string="BigCommerce Store"
    )
    bigcommerce_category_id = fields.Integer("BigCommerce Category ID")
    bigcommerce_tree_id = fields.Integer("Tree ID")
    bigcommerce_parent_id = fields.Integer("Parent ID")
    views = fields.Integer("Views")
    sort_order = fields.Integer("Sort Order")
    page_title = fields.Char("Page Title")
    search_keywords = fields.Char("Search Keywords")
    layout_file = fields.Char("Layout File")
    is_visible = fields.Boolean("Is Visible")
    default_product_sort = fields.Char("Default Product Sort")
    url_path = fields.Char("URL Path")
    is_url_customized = fields.Boolean("Is URL Customized")
    image_url = fields.Char("Image URL")

    def action_update_category_in_bigcommerce(self):
        """ Update category in BigCommerce for the current record """
        self.ensure_one()

        store = self.bigcommerce_store_id
        if not store or not store.access_token or not store.store_hash:
            raise UserError("Missing BigCommerce store credentials.")

        if not self.bigcommerce_category_id:
            raise UserError("No BigCommerce Category ID found to update.")

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/trees/categories"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = [
            {
                "category_id": self.bigcommerce_category_id,
                "name": self.name,
                "tree_id": self.bigcommerce_tree_id,
                "parent_id": self.bigcommerce_parent_id,
                "views": self.views,
                "sort_order": self.sort_order,
                "page_title": self.page_title,
                "layout_file": self.layout_file,
                "image_url": self.image_url,
                "is_visible": self.is_visible,
                "search_keywords": self.search_keywords,
                "default_product_sort": self.default_product_sort,
                "url": {
                    "path": self.url_path or "",
                    "is_customized": self.is_url_customized,
                },
            }
        ]

        response = requests.put(url, headers=headers, json=payload)
        if response.status_code not in [200, 201]:
            raise UserError(f"Failed to update category: {response.text}")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "BigCommerce Category Updated",
                "message": f"Category '{self.name}' updated successfully.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_delete_category_in_bigcommerce(self):
        """ Delete this category from BigCommerce """
        self.ensure_one()

        store = self.bigcommerce_store_id
        if not store or not store.access_token or not store.store_hash:
            raise UserError("Missing BigCommerce store credentials.")

        if not self.bigcommerce_category_id:
            raise UserError("No BigCommerce Category ID to delete.")

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/trees/categories"
        params = {"category_id:in": self.bigcommerce_category_id}
        headers = {"X-Auth-Token": store.access_token, "Accept": "application/json"}

        response = requests.delete(url, headers=headers, params=params)

        if response.status_code != 202:
            raise UserError(
                f"Failed to delete category from BigCommerce: {response.text}"
            )

        self.bigcommerce_category_id = False  # Clear the ID after deletion

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Category Deleted",
                "message": f"BigCommerce category '{self.name}' deleted successfully.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_bulk_update_categories_in_bigcommerce(self):
        for record in self:
            try:
                record.action_update_category_in_bigcommerce()
            except Exception as e:
                _logger.error(
                    "Failed to update BigCommerce category for record %s: %s",
                    record.id,
                    str(e),
                )
