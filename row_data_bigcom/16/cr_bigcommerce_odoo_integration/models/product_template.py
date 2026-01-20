# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import base64
from odoo.fields import Command
import logging
from io import BytesIO
from PIL import Image

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bigcommerce_store_id = fields.Many2one('bigcommerce.store', string="BigCommerce Store")
    bigcommerce_product_id = fields.Char("BigCommerce Product ID", store=True)
    bigcommerce_type = fields.Char("Product Type")
    bigcommerce_description = fields.Html("Description")
    bigcommerce_weight = fields.Float("Weight")
    bigcommerce_width = fields.Float("Width")
    bigcommerce_depth = fields.Float("Depth")
    bigcommerce_height = fields.Float("Height")
    bigcommerce_cost_price = fields.Float("Cost Price")
    bigcommerce_sale_price = fields.Float("Sale Price")
    bigcommerce_map_price = fields.Float("MAP Price")
    bigcommerce_tax_class_id = fields.Integer("Tax Class ID")
    bigcommerce_product_tax_code = fields.Char("Product Tax Code")
    bigcommerce_calculated_price = fields.Float("Calculated Price")
    bigcommerce_categories = fields.Char("Category IDs")
    bigcommerce_brand_id = fields.Many2one('bigcommerce.brand', "Brand ID")
    bigcommerce_option_set_id = fields.Integer("Option Set ID")
    bigcommerce_inventory_level = fields.Integer("Inventory Level")
    bigcommerce_tracking = fields.Char("Inventory Tracking")
    bigcommerce_total_sold = fields.Integer("Total Sold")
    bigcommerce_layout_file = fields.Char("Layout File")
    bigcommerce_upc = fields.Char("UPC")
    bigcommerce_mpn = fields.Char("MPN")
    bigcommerce_gtin = fields.Char("GTIN")
    bigcommerce_url = fields.Char("Product URL")
    bigcommerce_is_visible = fields.Boolean("Visible on Store")
    bigcommerce_availability = fields.Char("Availability")
    bigcommerce_condition = fields.Char("Condition")
    bigcommerce_page_title = fields.Char("Page Title")
    bigcommerce_meta_description = fields.Char("Meta Description")
    bigcommerce_view_count = fields.Integer("View Count")

    def import_product_image(self):
        store = self.bigcommerce_store_id
        product_id = self.bigcommerce_product_id
        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id}/images"
        headers = {
            'X-Auth-Token': store.access_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None

        images = response.json().get('data', [])
        for idx, img in enumerate(sorted(images, key=lambda i: i.get('sort_order', 0))):
            img_url = img.get('url_standard') or img.get('url_zoom')
            if not img_url:
                continue

            try:
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    img_data = base64.b64encode(img_response.content)
                    if idx == 0 or img.get('is_thumbnail'):
                        self.image_1920 = img_data  # Assign to main image
                    else:
                        self.env['product.image'].create({
                            'product_tmpl_id': self.id,
                            'image_1920': img_data,
                            'name': img.get('description') or 'BigCommerce Image'
                        })
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'success',
                            'title': _("Import Successfully"),
                            'message': _("Products Image Import Successfully."),
                            'sticky': False,
                            'next': {
                                'type': 'ir.actions.client',
                                'tag': 'soft_reload'
                            }
                        }
                    }
                return None
            except Exception:
                continue  # Optionally log errors
        return None

    def import_bigcommerce_variants(self):
        _logger.info(">>> Starting import_bigcommerce_variants for product ID: %s", self.bigcommerce_product_id)

        store = self.bigcommerce_store_id
        product_id = self.bigcommerce_product_id
        base_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id}/variants"

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        _logger.info("Fetching variants from BigCommerce URL: %s", base_url)

        response = requests.get(base_url, headers=headers)

        if response.status_code != 200:
            _logger.error("Failed to fetch variants from BigCommerce for product %s: %s", product_id, response.text)
            raise Exception(f"Failed to fetch variants: {response.text}")

        bigcommerce_variants = response.json().get('data', [])
        _logger.info("Fetched %d variant(s) from BigCommerce for product ID: %s", len(bigcommerce_variants), product_id)

        Product = self.env['product.product']
        Attribute = self.env['product.attribute']
        AttributeValue = self.env['product.attribute.value']
        TemplateAttributeLine = self.env['product.template.attribute.line']

        # Step 1: Extract attributes and values
        for variant in bigcommerce_variants:
            for option in variant.get('option_values', []):
                attr_name = option['option_display_name']
                attr_value = option['label']
                _logger.info("Processing attribute: %s = %s", attr_name, attr_value)

                attribute = Attribute.search([
                    ('name', '=', attr_name),
                    ('create_variant', '=', 'always')
                ], limit=1)
                if not attribute:
                    attribute = Attribute.create({
                        'name': attr_name,
                        'create_variant': 'always'
                    })
                    _logger.info("Created new attribute: %s", attr_name)

                value = AttributeValue.search([
                    ('name', '=', attr_value),
                    ('attribute_id', '=', attribute.id)
                ], limit=1)
                if not value:
                    value = AttributeValue.create({
                        'name': attr_value,
                        'attribute_id': attribute.id
                    })
                    _logger.info("Created new attribute value: %s (Attribute: %s)", attr_value, attr_name)

                attr_line = TemplateAttributeLine.search([
                    ('product_tmpl_id', '=', self.id),
                    ('attribute_id', '=', attribute.id)
                ], limit=1)

                if not attr_line:
                    TemplateAttributeLine.create({
                        'product_tmpl_id': self.id,
                        'attribute_id': attribute.id,
                        'value_ids': [Command.link(value.id)]
                    })
                    _logger.info("Created template attribute line for %s with value %s", attr_name, attr_value)
                elif value.id not in attr_line.value_ids.ids:
                    attr_line.value_ids = [Command.link(val.id) for val in attr_line.value_ids + value]
                    _logger.info("Updated attribute line %s with new value %s", attr_name, attr_value)

        # Step 2: Recompute product variants
        _logger.info("Recomputing product variants for product ID: %s", self.id)
        self._create_variant_ids()

        # Step 3: Match and assign variant info
        for variant in bigcommerce_variants:
            variant_option_names = {
                ov['option_display_name']: ov['label']
                for ov in variant.get('option_values', [])
            }
            _logger.info("Matching BigCommerce variant options: %s", variant_option_names)

            matched_variant = None
            for rec in self.product_variant_ids:
                matched = all(
                    variant_option_names.get(val.attribute_id.name) == val.name
                    for val in rec.product_template_attribute_value_ids
                )
                if matched:
                    matched_variant = rec
                    break

            if matched_variant:
                matched_variant.bigcommerce_store_id = self.bigcommerce_store_id.id
                matched_variant.bigcommerce_product_attribute_id = variant.get('id')
                matched_variant.bigcommerce_product_id = variant.get('product_id')
                matched_variant.bigcommerce_sku = variant.get('sku')
                matched_variant.bigcommerce_sku_id = variant.get('sku_id')
                matched_variant.default_code = variant.get('sku')

                _logger.info("Matched and updated variant SKU: %s (variant ID: %s)", variant.get('sku'),
                             variant.get('id'))
            else:
                _logger.warning("No matching variant found in Odoo for BigCommerce SKU: %s", variant.get('sku'))

        _logger.info("<<< Finished import_bigcommerce_variants for product ID: %s", product_id)

    def export_to_bigcommerce(self):
        for product in self:
            if not product.bigcommerce_store_id:
                raise UserError("Please select a BigCommerce Store for the product.")

            store = product.bigcommerce_store_id
            store_hash = store.store_hash
            access_token = store.access_token

            url = f"https://api.bigcommerce.com/stores/{store_hash}/v3/catalog/products"
            headers = {
                "X-Auth-Token": access_token,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            try:
                category_ids = (
                    [int(c.strip()) for c in product.bigcommerce_categories.split(',')]
                    if product.bigcommerce_categories else []
                )
            except Exception:
                raise UserError("Invalid category IDs. Ensure they are comma-separated integers.")

            payload = {
                "name": product.name,
                "type": product.bigcommerce_type or "physical",
                "sku": product.default_code or "",
                "description": product.bigcommerce_description or "",
                "weight": product.bigcommerce_weight or 0,
                "width": product.bigcommerce_width or None,
                "depth": product.bigcommerce_depth or None,
                "height": product.bigcommerce_height or None,
                "cost_price": product.bigcommerce_cost_price or 0,
                "price": product.bigcommerce_sale_price or product.list_price,
                "map_price": product.bigcommerce_map_price or None,
                "tax_class_id": product.bigcommerce_tax_class_id or None,
                "product_tax_code": product.bigcommerce_product_tax_code or "",
                "calculated_price": product.bigcommerce_calculated_price or None,
                "categories": category_ids,
                "brand_id": product.bigcommerce_brand_id or None,
                "option_set_id": product.bigcommerce_option_set_id or None,
                "inventory_level": product.bigcommerce_inventory_level or int(product.qty_available),
                "inventory_tracking": product.bigcommerce_tracking or "product",
                "layout_file": product.bigcommerce_layout_file or "",
                "upc": product.bigcommerce_upc or "",
                "mpn": product.bigcommerce_mpn or "",
                "gtin": product.bigcommerce_gtin or "",
                "is_visible": product.bigcommerce_is_visible,
                "availability": product.bigcommerce_availability or "available",
                "condition": product.bigcommerce_condition or "New",
                "page_title": product.bigcommerce_page_title or "",
                "meta_description": product.bigcommerce_meta_description or ""
            }

            # Clean out keys with None values to prevent API errors
            payload = {k: v for k, v in payload.items() if v is not None}

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                product.bigcommerce_product_id = response_data['data']['id']
            else:
                raise UserError(f"Failed to export product:\n{response.status_code}\n{response.text}")

    def bigcommerce_update_product(self):
        for product in self:
            if not product.bigcommerce_product_id:
                raise UserError(_("Missing BigCommerce Product ID for product %s") % product.name)

            if not product.bigcommerce_store_id or not product.bigcommerce_store_id.store_hash or not product.bigcommerce_store_id.access_token:
                raise UserError(_("Missing BigCommerce store configuration for product %s") % product.name)

            url = f"https://api.bigcommerce.com/stores/{product.bigcommerce_store_id.store_hash}/v3/catalog/products/{product.bigcommerce_product_id}"
            headers = {
                "X-Auth-Token": product.bigcommerce_store_id.access_token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            # Construct payload
            payload = {
                "name": product.name,
                "type": product.bigcommerce_type or "physical",
                "sku": product.default_code or "",
                "description": product.bigcommerce_description or "",
                "weight": product.bigcommerce_weight or 0,
                "width": product.bigcommerce_width or 0,
                "depth": product.bigcommerce_depth or 0,
                "height": product.bigcommerce_height or 0,
                "price": product.bigcommerce_sale_price or 0,
                "cost_price": product.bigcommerce_cost_price or 0,
                "sale_price": product.bigcommerce_sale_price or 0,
                "map_price": product.bigcommerce_map_price or 0,
                "tax_class_id": product.bigcommerce_tax_class_id or 0,
                "product_tax_code": product.bigcommerce_product_tax_code or "",
                "categories": [int(c) for c in
                               product.bigcommerce_categories.split(',')] if product.bigcommerce_categories else [],
                "inventory_level": product.bigcommerce_inventory_level or int(product.qty_available),
                "inventory_tracking": product.bigcommerce_tracking or "product",
                "layout_file": product.bigcommerce_layout_file or "",
                "upc": product.bigcommerce_upc or "",
                "mpn": product.bigcommerce_mpn or "",
                "gtin": product.bigcommerce_gtin or "",
                "is_visible": product.bigcommerce_is_visible,
                "availability": product.bigcommerce_availability or "available",
                "condition": product.bigcommerce_condition or "New",
                "page_title": product.bigcommerce_page_title or "",
                "meta_description": product.bigcommerce_meta_description or "",
            }

            response = requests.put(url, headers=headers, data=json.dumps(payload))
            if response.status_code not in [200, 201]:
                raise UserError(_("Failed to update product in BigCommerce: %s") % response.text)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "BigCommerce Product Updated",
                'message': f"Product '{self.name}' updated successfully.",
                'type': 'success',
                'sticky': False,
            }
        }

    def action_delete_product_from_bigcommerce(self):
        self.ensure_one()

        if not self.bigcommerce_product_id or not self.bigcommerce_store_id:
            raise UserError("Missing BigCommerce Product ID or Store.")

        store = self.bigcommerce_store_id

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{self.bigcommerce_product_id}"

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            # Optionally unlink the BigCommerce product ID after deletion
            self.bigcommerce_product_id = False

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "BigCommerce Product Deleted",
                    'message': f"Product '{self.name}' deleted successfully from BigCommerce.",
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(f"Failed to delete product from BigCommerce: {response.status_code} - {response.text}")

    def export_bigcommerce_product_images(self):
        if not self.bigcommerce_product_id or not self.bigcommerce_store_id:
            raise UserError("Product must be exported to BigCommerce first.")

        store = self.bigcommerce_store_id
        product_id = self.bigcommerce_product_id

        # Prepare main image (image_1920)
        if self.image_1920:
            img_binary = base64.b64decode(self.image_1920)
            files = {
                'image_file': ('main_image.jpg', img_binary, 'image/jpeg'),
            }

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id}/images"
            headers = {
                'X-Auth-Token': store.access_token,
                'Accept': 'application/json',
            }

            response = requests.post(url, headers=headers, files=files)
            if response.status_code != 200:
                raise UserError(f"Failed to upload main image: {response.text}")

    def create_bigcommerce_product_option(self, product_id, attribute):
        store = self.bigcommerce_store_id
        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id.bigcommerce_product_id}/options"
        headers = {
            'X-Auth-Token': store.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            "display_name": attribute.name,
            "type": "dropdown",  # Use 'dropdown', 'radio_buttons', 'swatch', etc. based on UI preference
            "option_values": [{"label": val.name} for val in attribute.value_ids]
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json().get('data')
            attribute.bigcommerce_option_id = data['id']  # Save option_id to attribute

            # Save value IDs
            option_value_map = {v['label']: v['id'] for v in data.get('option_values', [])}
            for val in attribute.value_ids:
                val.bigcommerce_value_id = option_value_map.get(val.name)

            return data['id']
        else:
            raise UserError(
                f"Failed to export product option to BigCommerce:\n{response.status_code} - {response.text}")

    def export_bigcommerce_variant(self, product_id, variant):
        store = self.bigcommerce_store_id
        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id.bigcommerce_product_id}/variants"
        headers = {
            'X-Auth-Token': store.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        option_values = []
        for ptav in variant.product_template_attribute_value_ids:
            option_id = ptav.attribute_id.bigcommerce_option_id
            value_id = ptav.product_attribute_value_id.bigcommerce_value_id
            if not option_id or not value_id:
                raise UserError(f"Missing option_id or value_id for {ptav.display_name}")
            option_values.append({
                "option_id": option_id,
                "id": value_id
            })

        payload = {
            "sku": variant.default_code or variant.name,
            "option_values": option_values,
            "price": variant.lst_price or 0.0,
            # "inventory_level": int(variant.qty_available or 0),
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()['data']
            variant.bigcommerce_store_id = store.id
            variant.bigcommerce_product_attribute_id = data['id']
            variant.bigcommerce_product_id = data['product_id']
            variant.bigcommerce_sku = data['sku']
            variant.bigcommerce_sku_id = data['sku_id']

            # Add variant image if available
            if variant.image_1920:
                # Prepare main image (image_1920)
                if variant.image_1920:
                    img_binary = base64.b64decode(variant.image_1920)
                    files = {
                        'image_file': ('main_image.jpg', img_binary, 'image/jpeg'),
                    }

                    url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id.bigcommerce_product_id}/variants/{data['id']}/image"
                    headers = {
                        'X-Auth-Token': store.access_token,
                        'Accept': 'application/json',
                    }

                    response = requests.post(url, headers=headers, files=files)
                    if response.status_code != 200:
                        raise UserError(f"Failed to upload main image: {response.text}")
            return data['id']
        else:
            raise UserError(f"Variant export failed: {response.text}")

    def action_bulk_export_to_bigcommerce(self):
        for product in self:
            product.export_to_bigcommerce()

    def action_bulk_update_bigcommerce_product(self):
        for product in self:
            product.bigcommerce_update_product()


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    bigcommerce_option_id = fields.Integer("BigCommerce Option ID")


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    bigcommerce_value_id = fields.Integer("BigCommerce Value ID")


