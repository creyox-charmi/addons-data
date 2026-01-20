# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class BigCommerceBrand(models.Model):
    _name = "bigcommerce.brand"
    _description = "BigCommerce Brand"

    name = fields.Char(required=True)
    brand_id = fields.Integer("BigCommerce Brand ID", readonly=True)
    page_title = fields.Char()
    meta_keywords = fields.Char()
    meta_description = fields.Text()
    image_url = fields.Char()
    search_keywords = fields.Char()
    custom_url = fields.Char()
    is_customized_url = fields.Boolean()
    store_id = fields.Many2one("bigcommerce.store", string="Store", required=True)

    def action_update_brand_on_bigcommerce(self):
        """Update this brand record in BigCommerce."""
        self.ensure_one()

        if not self.store_id.access_token or not self.store_id.store_hash:
            raise UserError(_("Missing BigCommerce API credentials."))

        if not self.brand_id:
            raise UserError(_("No BigCommerce Brand ID found for update."))

        url = f"https://api.bigcommerce.com/stores/{self.store_id.store_hash}/v3/catalog/brands/{self.brand_id}"
        headers = {
            "X-Auth-Token": self.store_id.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = {"name": self.name}

        # Optional fields
        if self.page_title:
            payload["page_title"] = str(self.page_title)
        if self.meta_description:
            payload["meta_description"] = str(self.meta_description)
        if self.search_keywords:
            payload["search_keywords"] = str(self.search_keywords)
        if self.image_url:
            payload["image_url"] = str(self.image_url)
        if self.meta_keywords:
            payload["meta_keywords"] = [
                kw.strip() for kw in self.meta_keywords.split(",") if kw.strip()
            ]
        if self.custom_url:
            payload["custom_url"] = {
                "url": str(self.custom_url),
                "is_customized": bool(self.is_customized_url),
            }

        response = requests.put(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Brand Updated"),
                    "message": _("Brand updated successfully on BigCommerce."),
                    "type": "success",
                    "sticky": False,
                },
            }
        else:
            _logger.error("BigCommerce Brand Update Failed: %s", response.text)
            raise UserError(
                _("Failed to update brand on BigCommerce: %s") % response.text
            )

    def action_delete_brand_from_bigcommerce(self):
        """Delete the brand from BigCommerce via API."""
        self.ensure_one()

        if not self.brand_id:
            raise UserError(_("No BigCommerce Brand ID found."))

        if not self.store_id.access_token or not self.store_id.store_hash:
            raise UserError(_("Missing BigCommerce API credentials."))

        url = f"https://api.bigcommerce.com/stores/{self.store_id.store_hash}/v3/catalog/brands/{self.brand_id}"
        headers = {
            "X-Auth-Token": self.store_id.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.delete(url, headers=headers)

        if response.status_code in [204]:  # 204 No Content means success
            self.brand_id = False
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Brand Deleted"),
                    "message": _("Brand deleted successfully from BigCommerce."),
                    "type": "success",
                    "sticky": False,
                },
            }
        else:
            _logger.error("BigCommerce Brand Delete Failed: %s", response.text)
            raise UserError(
                _("Failed to delete brand from BigCommerce: %s") % response.text
            )

    def action_bulk_update_brand_on_bigcommerce(self):
        for brand in self:
            try:
                brand.action_update_brand_on_bigcommerce()
            except Exception as e:
                _logger.exception("Failed to update brand %s: %s", brand.name, str(e))
