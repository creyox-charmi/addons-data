# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import math
from odoo.addons.payment import utils as payment_utils
import io
import logging
import mimetypes
import requests
import json
from odoo.tools import config
from urllib.parse import urlparse
from collections import defaultdict
from odoo.exceptions import ValidationError
from collections import defaultdict

_logger = logging.getLogger(__name__)


class BigCommerceStore(models.Model):
    _name = "bigcommerce.store"
    _description = "Bigcommerce Store"

    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char(string="Client Secret")
    access_token = fields.Char(string="Access Token")
    api_url = fields.Char(string="API URL")
    store_hash = fields.Char(string="Store Hash")
    bigcommerce_id = fields.Char("Big Commerce Id")
    store_id = fields.Char(string="Store ID")
    account_uuid = fields.Char(string="Account UUID")
    name = fields.Char(string="Store Name")
    domain = fields.Char(string="Primary Domain")
    secure_url = fields.Char(string="Secure URL")
    control_panel_base_url = fields.Char(string="Control Panel URL")
    status = fields.Char(string="Store Status")
    first_name = fields.Char(string="Contact First Name")
    last_name = fields.Char(string="Contact Last Name")
    address = fields.Char(string="Address")
    country = fields.Char(string="Country")
    country_code = fields.Char(string="Country Code")
    infrastructure_region = fields.Char(string="Infrastructure Region")
    phone = fields.Char(string="Phone Number")
    admin_email = fields.Char(string="Admin Email")
    order_email = fields.Char(string="Order Email")
    favicon_url = fields.Char(string="Favicon URL")

    language = fields.Char(string="Language")
    currency = fields.Char(string="Currency")
    currency_symbol = fields.Char(string="Currency Symbol")
    decimal_separator = fields.Char(string="Decimal Separator")
    thousands_separator = fields.Char(string="Thousands Separator")
    decimal_places = fields.Integer(string="Decimal Places")
    currency_symbol_location = fields.Selection(
        [("left", "Left"), ("right", "Right")], string="Currency Symbol Location"
    )

    weight_units = fields.Char(string="Weight Units")
    dimension_units = fields.Char(string="Dimension Units")
    dimension_decimal_places = fields.Integer(string="Dimension Decimal Places")
    dimension_decimal_token = fields.Char(string="Dimension Decimal Token")
    dimension_thousands_token = fields.Char(string="Dimension Thousands Token")

    plan_name = fields.Char(string="Plan Name")
    plan_level = fields.Char(string="Plan Level")
    plan_is_trial = fields.Boolean(string="Is Trial Plan")
    industry = fields.Char(string="Industry")

    logo_url = fields.Char(string="Logo URL")
    is_price_entered_with_tax = fields.Boolean(string="Prices Entered with Tax")

    default_channel_id = fields.Integer(string="Default Channel ID")
    default_site_id = fields.Integer(string="Default Site ID")

    active_comparison_modules = fields.Char(string="Active Comparison Modules")
    connection_status = fields.Selection(
        [("draft", "Draft"), ("fail", "Failed"), ("connected", "Connected")],
        string="Connection Status",
        default="draft",
    )
    product_category_ids = fields.One2many(
        "product.category", "bigcommerce_store_id", string="Product Categories"
    )
    product_template_ids = fields.One2many(
        "product.template", "bigcommerce_store_id", string="Products"
    )
    partner_ids = fields.One2many(
        "res.partner", "bigcommerce_store_id", string="Customers"
    )
    sale_order_ids = fields.One2many(
        "sale.order", "bigcommerce_store_id", string="Orders"
    )
    inventory_location_ids = fields.One2many(
        "bigcommerce.inventory.location",
        "bigcommerce_store_id",
        string="Inventory Locations",
    )
    webhook_ids = fields.One2many(
        "bigcommerce.webhook", "bigcommerce_store_id", string="Webhooks"
    )
    order_sequence = fields.Char(string="Enter Custom sequence")
    auto_import_product = fields.Boolean(string="Auto Import Product")
    auto_import_order = fields.Boolean(string="Auto Import Order")
    import_cron_value = fields.Integer(string="Import Cron Value")
    import_scheduled_units = fields.Selection(
        [
            ("hours", "Hours"),
            ("minutes", "Minute"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Import Cron Units",
        default="hours",
    )

    import_cron_value1 = fields.Integer(string="Import Cron Value")
    import_scheduled_units1 = fields.Selection(
        [
            ("hours", "Hours"),
            ("minutes", "Minute"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Import Cron Units",
        default="hours",
    )
    cr_logs_ids = fields.One2many("cr.data.processing.log", "cr_shop_id", string="Logs")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    total_customers = fields.Integer(
        string="Total Customers", compute="_compute_totals", store=True
    )
    total_orders = fields.Integer(
        string="Total Orders", compute="_compute_totals", store=True
    )
    total_products = fields.Integer(
        string="Total Products", compute="_compute_totals", store=True
    )
    total_shipped_orders = fields.Integer(
        string="Shipped Orders", compute="_compute_totals", store=True
    )
    total_refunded_orders = fields.Integer(
        string="Refunded Orders", compute="_compute_totals", store=True
    )
    auto_create_customer = fields.Boolean(
        string="Auto-create Customer if Missing", default=True
    )
    auto_create_product = fields.Boolean(
        string="Auto-create Product if Missing", default=True
    )
    default_product_category_id = fields.Many2one(
        'product.category',
        string='Default Product Category',
        domain="[('bigcommerce_store_id', '=', id)]",
        help='Category to assign to products that have no category in BigCommerce'
    )


    def action_open_import_wizard(self):
        return {
            "name": "Import Data",
            "type": "ir.actions.act_window",
            "res_model": "bigcommerce.import.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_store_id": self.id},
        }

    def action_open_export_wizard(self):
        return {
            "name": "Export Data",
            "type": "ir.actions.act_window",
            "res_model": "bigcommerce.export.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_store_id": self.id},
        }

    @api.depends("partner_ids", "sale_order_ids", "product_template_ids")
    def _compute_totals(self):
        for record in self:
            record.total_customers = len(record.partner_ids)
            record.total_orders = len(record.sale_order_ids)
            record.total_products = len(record.product_template_ids)
            record.total_shipped_orders = len(
                record.sale_order_ids.filtered(lambda o: o.state == "done")
            )
            record.total_refunded_orders = len(
                record.sale_order_ids.filtered(
                    lambda o: o.invoice_status == "invoiced"
                    and any(inv.move_type == "out_refund" for inv in o.invoice_ids)
                )
            )

    def action_sync_store_info(self):
        count = 0
        fail = 0
        for record in self:
            if record.company_id and record.company_id != self.env.company:
                continue  # or raise UserError(_("You cannot sync a store that doesn't belong to your current company."))

            # Ensure required credentials exist
            if not all([record.access_token, record.api_url, record.store_hash]):
                raise UserError(
                    _("Please fill in Access Token, API URL, and Store Hash.")
                )

            url = f"https://api.bigcommerce.com/stores/{record.store_hash}/v2/store"
            headers = {
                "X-Auth-Token": record.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            try:
                response = requests.get(url, headers=headers, timeout=20)
                if response.status_code == 200:
                    data = response.json()

                    record.write(
                        {
                            "bigcommerce_id": data.get("id"),
                            "account_uuid": data.get("account_uuid"),
                            "domain": data.get("domain"),
                            "secure_url": data.get("secure_url"),
                            "control_panel_base_url": data.get(
                                "control_panel_base_url"
                            ),
                            "status": data.get("status"),
                            "name": data.get("name"),
                            "first_name": data.get("first_name"),
                            "last_name": data.get("last_name"),
                            "address": data.get("address"),
                            "country": data.get("country"),
                            "country_code": data.get("country_code"),
                            "infrastructure_region": data.get("infrastructure_region"),
                            "phone": data.get("phone"),
                            "admin_email": data.get("admin_email"),
                            "order_email": data.get("order_email"),
                            "favicon_url": data.get("favicon_url"),
                            "language": data.get("language"),
                            "currency": data.get("currency"),
                            "currency_symbol": data.get("currency_symbol"),
                            "decimal_separator": data.get("decimal_separator"),
                            "thousands_separator": data.get("thousands_separator"),
                            "decimal_places": data.get("decimal_places"),
                            "currency_symbol_location": data.get(
                                "currency_symbol_location"
                            ),
                            "weight_units": data.get("weight_units"),
                            "dimension_units": data.get("dimension_units"),
                            "dimension_decimal_places": data.get(
                                "dimension_decimal_places"
                            ),
                            "dimension_decimal_token": data.get(
                                "dimension_decimal_token"
                            ),
                            "dimension_thousands_token": data.get(
                                "dimension_thousands_token"
                            ),
                            "plan_name": data.get("plan_name"),
                            "plan_level": data.get("plan_level"),
                            "plan_is_trial": data.get("plan_is_trial"),
                            "industry": data.get("industry"),
                            "logo_url": data.get("logo")[0].get("url")
                            if isinstance(data.get("logo"), list) and data.get("logo")
                            else "",
                            "is_price_entered_with_tax": data.get(
                                "is_price_entered_with_tax"
                            ),
                            "store_id": data.get("store_id"),
                            "default_site_id": data.get("default_site_id"),
                            "default_channel_id": data.get("default_channel_id"),
                            "active_comparison_modules": json.dumps(
                                data.get("active_comparison_modules", [])
                            ),
                            "connection_status": "connected",
                        }
                    )
                    count += 1

                else:
                    fail += 1
                    record.connection_status = "fail"
                    raise UserError(
                        _(
                            "Failed to connect to BigCommerce API. Status Code: %s\nResponse: %s"
                        )
                        % (response.status_code, response.text)
                    )

                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Successfully fetched store data",
                    record_count=count,
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    cr_user_id=self.env.uid,
                )

            except Exception as e:
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Unsuccessful in fetching store data",
                    record_count=fail,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=str(e),
                    cr_user_id=self.env.uid,
                )
                record.connection_status = "fail"
                raise UserError(_("Error during synchronization: %s") % str(e))

    def import_bigcommerce_products(self):

        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time

        created_count = 0
        skipped_count = 0
        fail_count = 0

        for store in self:
            if not store.default_product_category_id:
                raise UserError(
                    "Default Product Category is not configured!\n\n"
                    "Please set a Default Product Category in the store settings before importing products.\n"
                    "This category will be assigned to products that have no category in BigCommerce."
                )
            start_time = time.time()

            try:
                headers = {
                    "X-Auth-Token": store.access_token,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }

                all_products = []
                page = 1
                limit = 250

                while True:
                    url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products"
                    params = {"page": page, "limit": limit}

                    try:
                        response = requests.get(url, headers=headers, params=params, timeout=30)

                        if response.status_code == 200:
                            response_data = response.json()
                            data = response_data.get("data", [])

                            if not data:
                                break

                            all_products.extend(data)
                            pagination = response_data.get("meta", {}).get("pagination", {})

                            if pagination.get("current_page", page) >= pagination.get("total_pages", page):
                                break

                            page += 1
                            time.sleep(0.1)

                        elif response.status_code == 429:
                            time.sleep(30)
                            continue
                        else:
                            break

                    except Exception as e:
                        break

                if not all_products:
                    continue

                try:
                    product_ids = [p.get("id") for p in all_products if p.get("id")]

                    all_existing_products = self.env["product.template"].search([
                        ("bigcommerce_product_id", "in", product_ids),
                        ("bigcommerce_store_id", "=", store.id),
                    ])

                    existing_ids = set(all_existing_products.mapped("bigcommerce_product_id"))

                    existing_products_map = {
                        p.bigcommerce_product_id: p.id
                        for p in all_existing_products
                    }

                    products_to_create = []
                    skipped_in_phase2 = 0

                    for p in all_products:
                        product_bc_id = p.get("id")

                        if product_bc_id in existing_ids:
                            skipped_in_phase2 += 1

                        else:
                            products_to_create.append(p)

                    skipped_count += skipped_in_phase2

                except Exception as e:
                    self.env.cr.rollback()
                    products_to_create = all_products

                if not products_to_create:
                    continue

                try:
                    # Get or create DEFAULT category
                    default_category = self.env["product.category"].search([
                        ("name", "=", "General"),
                        ("bigcommerce_store_id", "=", store.id),
                    ], limit=1)

                    if not default_category:
                        default_category = self.default_product_category_id.id
                        self.env.cr.commit()

                    default_category_id = default_category.id

                    all_categories = self.env["product.category"].search([
                        ("bigcommerce_store_id", "=", store.id),
                    ])
                    category_map = {cat.bigcommerce_category_id: cat.id for cat in all_categories}

                    shop_all_category_id = next(
                        (cat.id for cat in all_categories if cat.name and "shop all" in cat.name.lower()),
                        False
                    )

                    all_brands = self.env["bigcommerce.brand"].search([
                        ("store_id", "=", store.id),
                    ])
                    brand_map = {brand.brand_id: brand.id for brand in all_brands}

                except Exception as e:
                    self.env.cr.rollback()
                    try:
                        default_category = self.env["product.category"].create({"name": "General"})
                        default_category_id = default_category.id
                        self.env.cr.commit()
                    except:
                        default_category_id = 1
                    category_map = {}
                    brand_map = {}
                    shop_all_category_id = False

                products_vals_list = []

                for item in products_to_create:
                    bc_id = item['id']

                    create_bool = 1
                    for ex_id in existing_ids:
                        if str(ex_id) == str(bc_id):
                            create_bool = 0

                    if create_bool:
                        try:
                            category_ids = [
                                category_map[cat_id]
                                for cat_id in item.get("categories", [])
                                if cat_id in category_map and category_map.get(cat_id) != shop_all_category_id
                            ]

                            final_category_id = category_ids[0] if category_ids else default_category_id
                            brand_rec_id = brand_map.get(item.get("brand_id"), False)

                            products_vals_list.append({
                                "name": item.get("name", "Unnamed Product"),
                                "bigcommerce_store_id": store.id,
                                "bigcommerce_product_id": item.get("id"),
                                "default_code": item.get("sku"),
                                "list_price": item.get("price", 0.0),
                                "bigcommerce_type": item.get("type"),
                                "bigcommerce_description": item.get("description"),
                                "bigcommerce_weight": item.get("weight"),
                                "bigcommerce_width": item.get("width"),
                                "bigcommerce_depth": item.get("depth"),
                                "bigcommerce_height": item.get("height"),
                                "bigcommerce_cost_price": item.get("cost_price"),
                                "bigcommerce_sale_price": item.get("sale_price"),
                                "bigcommerce_map_price": item.get("map_price"),
                                "bigcommerce_tax_class_id": item.get("tax_class_id"),
                                "bigcommerce_product_tax_code": item.get("product_tax_code"),
                                "bigcommerce_calculated_price": item.get("calculated_price"),
                                "bigcommerce_categories": ",".join(map(str, item.get("categories", []))),
                                "bigcommerce_brand_id": brand_rec_id if brand_rec_id else False,
                                "bigcommerce_option_set_id": item.get("option_set_id"),
                                "bigcommerce_inventory_level": item.get("inventory_level"),
                                "bigcommerce_tracking": item.get("inventory_tracking"),
                                "bigcommerce_total_sold": item.get("total_sold"),
                                "bigcommerce_layout_file": item.get("layout_file"),
                                "bigcommerce_upc": item.get("upc"),
                                "bigcommerce_mpn": item.get("mpn"),
                                "bigcommerce_gtin": item.get("gtin"),
                                "bigcommerce_url": item.get("custom_url", {}).get("url"),
                                "bigcommerce_is_visible": item.get("is_visible"),
                                "bigcommerce_availability": item.get("availability"),
                                "bigcommerce_condition": item.get("condition"),
                                "bigcommerce_page_title": item.get("page_title"),
                                "bigcommerce_meta_description": item.get("meta_description"),
                                "bigcommerce_view_count": item.get("view_count"),
                                "categ_id": final_category_id,
                                "company_id": store.company_id.id,
                                "type": "consu",
                                "is_storable": True,
                            })

                        except Exception as e:
                            fail_count += 1
                    else:
                        continue

                batch_size = 50
                store_created = 0
                store_failed = 0
                store_skipped_during_create = 0
                created_product_ids = []

                total_batches = (len(products_vals_list) + batch_size - 1) // batch_size

                for batch_idx in range(0, len(products_vals_list), batch_size):
                    batch = products_vals_list[batch_idx:batch_idx + batch_size]
                    batch_num = (batch_idx // batch_size) + 1

                    batch_bc_ids = [p["bigcommerce_product_id"] for p in batch]

                    try:
                        just_before_create_check = self.env["product.template"].search([
                            ("bigcommerce_product_id", "in", batch_bc_ids),
                            ("bigcommerce_store_id", "=", store.id),
                        ])

                        if just_before_create_check:
                            newly_found_ids = set(just_before_create_check.mapped("bigcommerce_product_id"))

                            batch = [p for p in batch if p["bigcommerce_product_id"] not in newly_found_ids]
                            store_skipped_during_create += len(newly_found_ids)

                        if not batch:
                            continue

                    except Exception as e:

                        self.env.cr.rollback()

                    try:
                        created_products = self.env["product.template"].create(batch)
                        store_created += len(created_products)
                        created_product_ids.extend(created_products.ids)

                        self.env.cr.commit()

                    except Exception as e:
                        error_msg = str(e)

                        # Check if it's a duplicate constraint error
                        if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                            store_skipped_during_create += len(batch)
                        else:
                            store_failed += len(batch)

                        self.env.cr.rollback()

                        for single_vals in batch:
                            try:
                                individual_check = self.env["product.template"].search([
                                    ("bigcommerce_product_id", "=", single_vals["bigcommerce_product_id"]),
                                    ("bigcommerce_store_id", "=", store.id),
                                ], limit=1)

                                if individual_check:

                                    store_skipped_during_create += 1
                                    if "duplicate" in error_msg.lower():
                                        store_failed -= 1
                                    continue

                                single_product = self.env["product.template"].create(single_vals)
                                created_product_ids.append(single_product.id)
                                self.env.cr.commit()
                                store_created += 1
                                if not ("duplicate" in error_msg.lower()):
                                    store_failed -= 1

                            except Exception as single_error:
                                single_error_msg = str(single_error)
                                if "duplicate" in single_error_msg.lower() or "unique" in single_error_msg.lower():

                                    store_skipped_during_create += 1
                                    if not ("duplicate" in error_msg.lower()):
                                        store_failed -= 1
                                self.env.cr.rollback()

                creation_time = time.time() - start_time

                image_start = time.time()

                if store_created > 0 and created_product_ids:
                    try:
                        created_product_records = self.env["product.template"].browse(created_product_ids)

                        def process_product_image_variant(product):
                            """Process single product's images and variants"""
                            try:
                                with self.pool.cursor() as new_cr:
                                    new_env = self.env(cr=new_cr)
                                    product_in_thread = new_env["product.template"].browse(product.id)

                                    product_in_thread.import_product_image()
                                    product_in_thread.import_bigcommerce_variants()

                                    new_cr.commit()
                                    return {"success": True, "product_id": product.id}
                            except Exception as e:
                                try:
                                    new_cr.rollback()
                                except:
                                    pass
                                return {"success": False, "product_id": product.id, "error": str(e)[:50]}

                        img_success = 0
                        img_failed = 0

                        with ThreadPoolExecutor(max_workers=10) as executor:
                            futures = {
                                executor.submit(process_product_image_variant, product): product
                                for product in created_product_records
                            }

                            for idx, future in enumerate(as_completed(futures), 1):
                                result = future.result()

                                if result["success"]:
                                    img_success += 1
                                else:
                                    img_failed += 1


                        image_time = time.time() - image_start


                    except Exception as e:
                        image_time = time.time() - image_start
                else:
                    image_time = 0

                created_count += store_created
                skipped_count += store_skipped_during_create
                fail_count += store_failed

                total_elapsed = time.time() - start_time

                try:
                    self.env["cr.data.processing.log"].sudo()._log_data_processing(
                        cr_shop_id=self.id,
                        cr_message=f"Import: {store_created} created, {skipped_in_phase2 + store_skipped_during_create} duplicates skipped, {store_failed} failed in {total_elapsed:.2f}s",
                        record_count=store_created,
                        status="success" if store_failed == 0 else "partial",
                        timespan=str(fields.Datetime.now()),
                        initiated_at=str(fields.Datetime.now()),
                        cr_user_id=self.env.uid,
                    )
                    self.env.cr.commit()
                except:
                    self.env.cr.rollback()

            except Exception as e:

                import traceback
                traceback.print_exc()
                self.env.cr.rollback()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success" if fail_count == 0 else "warning",
                "title": _("Import Complete - NO Duplicates"),
                "message": _(
                    "Products: %d created, %d skipped (duplicates), %d failed."
                    % (created_count, skipped_count, fail_count)
                ),
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "soft_reload"},
            },
        }



    def action_import_bigcommerce_categories(self):
        count = 0
        fail = 0
        for store in self:
            if not all([store.store_hash, store.api_url, store.access_token]):
                raise UserError("Store Hash, API URL, and Access Token are required.")

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/trees/categories"
            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    raise UserError(f"Error {response.status_code}: {response.text}")

                data = response.json().get("data", [])
                shop_all_category = None

                for cat in data:
                    vals = {
                        "name": cat["name"],
                        "bigcommerce_category_id": cat["category_id"],
                        "bigcommerce_store_id": store.id,
                        "bigcommerce_tree_id": cat.get("tree_id"),
                        "bigcommerce_parent_id": cat.get("parent_id"),
                        "views": cat.get("views"),
                        "sort_order": cat.get("sort_order"),
                        "page_title": cat.get("page_title"),
                        "search_keywords": cat.get("search_keywords"),
                        "layout_file": cat.get("layout_file"),
                        "is_visible": cat.get("is_visible"),
                        "default_product_sort": cat.get("default_product_sort"),
                        "url_path": cat.get("url", {}).get("path"),
                        "is_url_customized": cat.get("url", {}).get("is_customized"),
                        "image_url": cat.get("image_url"),
                    }

                    existing = self.env["product.category"].search(
                        [
                            ("bigcommerce_category_id", "=", cat["category_id"]),
                            ("bigcommerce_store_id", "=", store.id),
                        ],
                        limit=1,
                    )

                    if existing:
                        existing.write(vals)
                    else:
                        count += 1
                        existing = self.env["product.category"].create(vals)

                    if cat["name"].strip().lower() == "shop all":
                        shop_all_category = existing

                if shop_all_category:
                    children = self.env["product.category"].search(
                        [
                            ("bigcommerce_store_id", "=", store.id),
                            ("id", "!=", shop_all_category.id),
                            ("parent_id", "=", False),
                            ("name", "!=", "All"),
                        ]
                    )
                    children.write({"parent_id": shop_all_category.id})

                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Sucessfully fetched product category",
                    record_count=count,
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    cr_user_id=self.env.uid,
                )
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "type": "success",
                        "title": _("Import Successfully"),
                        "message": _("Product Category Import Successfully."),
                        "sticky": False,
                        "next": {"type": "ir.actions.client", "tag": "soft_reload"},
                    },
                }

            except Exception as e:
                fail += 1
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Unsucessfull to fetched product category",
                    record_count=fail,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=f"Failed to import categories:\n{str(e)}",
                    cr_user_id=self.env.uid,
                )
                raise UserError(f"Failed to import categories:\n{str(e)}")
        return None

    def action_import_bigcommerce_customers(self):
        """Ultra-fast parallel import of customers."""
        import time
        import concurrent.futures
        from psycopg2.extras import execute_values

        for store in self:
            if not all([store.store_hash, store.api_url, store.access_token]):
                raise UserError("Store Hash, API URL, and Access Token are required.")

            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            start_time = time.time()

            def parse_datetime(dt_str):
                if not dt_str:
                    return None
                if dt_str.endswith("Z"):
                    dt_str = dt_str[:-1]
                return dt_str.replace("T", " ")

            def fetch_page(page_num):
                """Fetch a single page of customers."""
                url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers?page={page_num}&limit=250"
                try:
                    response = requests.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        return response.json().get("data", [])
                except:
                    pass
                return []

            try:
                # Step 1: Get total count
                url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers?limit=1"
                response = requests.get(url, headers=headers)
                total = response.json().get("meta", {}).get("pagination", {}).get("total", 0)
                total_pages = (total // 250) + 1

                _logger.info(f"Starting import of {total} customers across {total_pages} pages")

                # Step 2: Fetch all pages in parallel (max 10 concurrent requests)
                all_customers = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_page = {executor.submit(fetch_page, page): page for page in range(1, total_pages + 1)}
                    for future in concurrent.futures.as_completed(future_to_page):
                        customers = future.result()
                        all_customers.extend(customers)
                        if len(all_customers) % 1000 == 0:
                            _logger.info(f"Fetched {len(all_customers)} customers...")

                _logger.info(f"Fetched all {len(all_customers)} customers in {time.time() - start_time:.2f}s")

                # Step 3: Get all existing customers in ONE query
                all_bc_ids = [c["id"] for c in all_customers]
                existing_customers = self.env["res.partner"].search([
                    ("bigcommerce_customer_id", "in", all_bc_ids),
                    ("bigcommerce_store_id", "=", store.id),
                ])
                existing_map = {c.bigcommerce_customer_id: c.id for c in existing_customers}

                # Step 4: Prepare bulk data
                to_create = []
                to_update = []

                for customer in all_customers:
                    vals = {
                        "bigcommerce_store_id": store.id,
                        "company_id": store.company_id.id,
                        "name": f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or "Unknown",
                        "email": customer.get("email"),
                        "phone": customer.get("phone"),
                        "bigcommerce_customer_id": customer.get("id"),
                        "bigcommerce_company": customer.get("company"),
                        "bigcommerce_group_id": customer.get("customer_group_id"),
                        "bigcommerce_notes": customer.get("notes"),
                        "bigcommerce_registration_ip": customer.get("registration_ip_address"),
                        "bigcommerce_tax_exempt_category": customer.get("tax_exempt_category"),
                        "bigcommerce_date_created": parse_datetime(customer.get("date_created")),
                        "bigcommerce_date_modified": parse_datetime(customer.get("date_modified")),
                        "bigcommerce_accepts_review_emails": customer.get(
                            "accepts_product_review_abandoned_cart_emails"),
                        "bigcommerce_origin_channel_id": customer.get("origin_channel_id"),
                    }

                    if customer["id"] in existing_map:
                        to_update.append((existing_map[customer["id"]], vals))
                    else:
                        to_create.append(vals)

                # Step 5: Bulk create
                created_count = 0
                if to_create:
                    created_partners = self.env["res.partner"].create(to_create)
                    created_count = len(created_partners)
                    _logger.info(f"Bulk created {created_count} customers")

                # Step 6: Bulk update
                updated_count = 0
                if to_update:
                    for partner_id, vals in to_update:
                        self.env["res.partner"].browse(partner_id).write(vals)
                        updated_count += 1
                    _logger.info(f"Bulk updated {updated_count} customers")

                elapsed = time.time() - start_time
                _logger.info(
                    f"Customer import completed in {elapsed:.2f}s. Created: {created_count}, Updated: {updated_count}")

                # Log success
                if created_count:
                    self.env["cr.data.processing.log"].sudo()._log_data_processing(
                        cr_shop_id=store.id,
                        cr_message=f"Successfully created {created_count} customers in {elapsed:.2f}s",
                        record_count=created_count,
                        status="success",
                        timespan=str(fields.Datetime.now()),
                        initiated_at=str(fields.Datetime.now()),
                        cr_user_id=self.env.uid,
                    )

                if updated_count:
                    self.env["cr.data.processing.log"].sudo()._log_data_processing(
                        cr_shop_id=store.id,
                        cr_message=f"Successfully updated {updated_count} customers in {elapsed:.2f}s",
                        record_count=updated_count,
                        status="success",
                        timespan=str(fields.Datetime.now()),
                        initiated_at=str(fields.Datetime.now()),
                        cr_user_id=self.env.uid,
                    )

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "type": "success",
                        "title": _("Import Successful"),
                        "message": _(
                            f"Imported {len(all_customers)} customers in {elapsed:.2f}s\nCreated: {created_count}, Updated: {updated_count}"),
                        "sticky": False,
                    },
                }

            except Exception as e:
                error_msg = f"Failed to import customers: {str(e)}"
                _logger.error(error_msg)

                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=store.id,
                    cr_message="Unsuccessful in fetching customers.",
                    record_count=1,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(error_msg)

        return None

    def action_import_bigcommerce_customer_addresses(self):
        """Ultra-fast parallel import of customer addresses."""
        import time
        import concurrent.futures

        for store in self:
            if not all([store.store_hash, store.api_url, store.access_token]):
                raise UserError("Store Hash, API URL, and Access Token are required.")

            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            start_time = time.time()

            def fetch_page(page_num):
                """Fetch a single page of addresses."""
                url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers/addresses?page={page_num}&limit=250"
                try:
                    response = requests.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        return response.json().get("data", [])
                except:
                    pass
                return []

            try:
                # Step 1: Get total count
                url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers/addresses?limit=1"
                response = requests.get(url, headers=headers)
                total = response.json().get("meta", {}).get("pagination", {}).get("total", 0)
                total_pages = (total // 250) + 1

                _logger.info(f"Starting import of {total} addresses across {total_pages} pages")

                # Step 2: Fetch all pages in parallel (max 10 concurrent requests)
                all_addresses = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_page = {executor.submit(fetch_page, page): page for page in range(1, total_pages + 1)}
                    for future in concurrent.futures.as_completed(future_to_page):
                        addresses = future.result()
                        all_addresses.extend(addresses)
                        if len(all_addresses) % 1000 == 0:
                            _logger.info(f"Fetched {len(all_addresses)} addresses...")

                _logger.info(f"Fetched all {len(all_addresses)} addresses in {time.time() - start_time:.2f}s")

                # Step 3: Pre-load all reference data
                all_countries = self.env["res.country"].search([])
                country_map = {c.code: c.id for c in all_countries}

                all_states = self.env["res.country.state"].search([])
                state_map = {}
                for state in all_states:
                    key = (state.name.lower(), state.country_id.id)
                    state_map[key] = state.id

                # Step 4: Get all partners in ONE query
                customer_ids = list(set([addr.get("customer_id") for addr in all_addresses if addr.get("customer_id")]))
                partners = self.env["res.partner"].search([
                    ("bigcommerce_customer_id", "in", customer_ids),
                    ("bigcommerce_store_id", "=", store.id)
                ])
                partner_map = {p.bigcommerce_customer_id: p for p in partners}

                # Step 5: Prepare and execute updates
                updated_count = 0
                skipped_count = 0

                for addr in all_addresses:
                    customer_id = addr.get("customer_id")
                    partner = partner_map.get(customer_id)

                    if not partner:
                        skipped_count += 1
                        continue

                    country_id = country_map.get(addr.get("country_code"))
                    state_id = None

                    if country_id and addr.get("state_or_province"):
                        state_name = addr.get("state_or_province", "").lower()
                        state_id = state_map.get((state_name, country_id))

                    partner.write({
                        'street': addr.get("address1"),
                        'street2': addr.get("address2"),
                        'city': addr.get("city"),
                        'zip': addr.get("postal_code"),
                        'country_id': country_id,
                        'state_id': state_id,
                    })

                    updated_count += 1

                    # Log progress every 1000
                    if updated_count % 1000 == 0:
                        _logger.info(f"Updated {updated_count} addresses...")

                elapsed = time.time() - start_time
                _logger.info(
                    f"Address import completed in {elapsed:.2f}s. Updated: {updated_count}, Skipped: {skipped_count}")

                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=store.id,
                    cr_message=f"Successfully updated {updated_count} addresses in {elapsed:.2f}s",
                    record_count=updated_count,
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    cr_user_id=self.env.uid,
                )

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "type": "success",
                        "title": _("Addresses Imported"),
                        "message": _(
                            f"Updated {updated_count} addresses in {elapsed:.2f}s\nSkipped: {skipped_count} (customer not found)"),
                        "sticky": False,
                    },
                }

            except Exception as e:
                error_msg = f"Failed to import addresses: {str(e)}"
                _logger.error(error_msg)

                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=store.id,
                    cr_message="Unsuccessfully to fetched customer address",
                    record_count=1,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(error_msg)

        return None

    def action_import_order_statuses(self):
        created = 0
        updated = 0
        fail = 0
        self.ensure_one()

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2/order_statuses"
        headers = {
            "X-Auth-Token": self.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            fail += 1
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsuccessful in fetching order statuses",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to import order statuses. Response:\n{response.text}",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                _("Failed to fetch order statuses from BigCommerce. Response: %s")
                % response.text
            )

        order_statuses = response.json()
        status_model = self.env["bigcommerce.order.status"]

        for status in order_statuses:
            vals = {
                "store_id": self.id,
                "bigcommerce_status_id": status.get("id"),
                "name": status.get("name"),
                "system_label": status.get("system_label"),
                "custom_label": status.get("custom_label"),
                "system_description": status.get("system_description"),
                "order": status.get("order"),
            }
            exist = status_model.search(
                [
                    ("bigcommerce_status_id", "=", status.get("id")),
                    ("store_id", "=", self.id),
                ],
                limit=1,
            )
            if exist:
                exist.write(vals)
                updated += 1
            else:
                status_model.create(vals)
                created += 1

        # Log message
        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message="Successfully imported order statuses: %d created, %d updated"
                       % (created, updated),
            record_count=created + updated,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )

        # UI Notification
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": _("Order Statuses Imported"),
                "message": _(
                    "Successfully imported order statuses (%d created, %d updated)."
                    % (created, updated)
                ),
                "sticky": False,
            },
        }

    def action_import_bigcommerce_brands(self):
        for store in self:
            if not store.access_token or not store.store_hash:
                raise UserError("Missing API credentials.")

            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/brands"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Unsuccessful to fetch brands.",
                    record_count=0,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=f"Failed to fetch brands: {response.text}",
                    cr_user_id=self.env.uid,
                )
                raise UserError(f"Failed to fetch brands: {response.text}")

            brand_model = self.env["bigcommerce.brand"]
            created_count = 0
            updated_count = 0

            for brand in response.json().get("data", []):
                existing_brand = brand_model.search([
                    ('brand_id', '=', brand["id"]),
                    ('store_id', '=', store.id)
                ], limit=1)

                brand_vals = {
                    "name": brand["name"],
                    "page_title": brand.get("page_title"),
                    "meta_keywords": ", ".join(brand.get("meta_keywords", [])),
                    "meta_description": brand.get("meta_description"),
                    "image_url": brand.get("image_url"),
                    "search_keywords": brand.get("search_keywords"),
                    "custom_url": brand.get("custom_url", {}).get("url"),
                    "is_customized_url": brand.get("custom_url", {}).get("is_customized", False),
                }

                if existing_brand:
                    existing_brand.write(brand_vals)
                    updated_count += 1
                else:
                    brand_vals.update({
                        "brand_id": brand["id"],
                        "store_id": store.id,
                    })
                    brand_model.create(brand_vals)
                    created_count += 1

            # Log for created brands
            if created_count:
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Successfully created new brand(s).",
                    record_count=created_count,
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    cr_user_id=self.env.uid,
                )

            # Log for updated brands
            if updated_count:
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Successfully updated existing brand(s).",
                    record_count=updated_count,
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    cr_user_id=self.env.uid,
                )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "title": _("Brands Imported"),
                    "message": _(
                        "Successfully created %d and updated %d brand(s)."
                        % (created_count, updated_count)
                    ),
                    "sticky": False,
                },
            }
        return None

    def action_import_bigcommerce_currencies(self):
        fail = 0
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            fail += 1
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to fetched currency.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Missing API credentials on the store record.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Missing API credentials on the store record."))

        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2/currencies"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            fail += 1
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to fetched currency.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to fetch brands: {response.text}",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Failed to fetch currencies: %s") % response.text)

        currencies = response.json()
        imported_count = 0

        currency_obj = self.env["res.currency"]

        for curr in currencies:
            # Convert list to comma-separated string for default_for_country_codes
            country_codes = ",".join(curr.get("default_for_country_codes", []))

            # Safely parse the 'last_updated' field
            last_updated_str = curr.get("last_updated")
            if last_updated_str:
                try:
                    last_updated_dt = datetime.strptime(
                        last_updated_str, "%Y-%m-%dT%H:%M:%SZ"
                    )
                    last_updated = fields.Datetime.to_string(last_updated_dt)
                except Exception:
                    last_updated = False
            else:
                last_updated = False

            vals = {
                "bc_currency_id": curr.get("id"),
                "bigcommerce_store_id": self.id,
                "bc_currency_code": curr.get("currency_code"),
                "bc_name": curr.get("name"),
                "bc_enabled": curr.get("enabled"),
                "bc_is_transactional": curr.get("is_transactional"),
                "bc_is_default": curr.get("is_default"),
                "bc_auto_update": curr.get("auto_update"),
                "bc_exchange_rate": curr.get("currency_exchange_rate"),
                "bc_token": curr.get("token"),
                "bc_token_location": curr.get("token_location"),
                "bc_decimal_places": curr.get("decimal_places"),
                "bc_decimal_token": curr.get("decimal_token"),
                "bc_thousands_token": curr.get("thousands_token"),
                "bc_default_for_country_codes": country_codes,
                "bc_country_iso2": curr.get("country_iso2"),
                "bc_last_updated": last_updated,
                "bc_use_default_name": curr.get("use_default_name"),
                "symbol": curr.get("token"),
            }

            name = curr.get("name")
            code = curr.get("currency_code")
            existing_currency = currency_obj.search([("name", "=", "INR")], limit=1)

            if not existing_currency:
                existing_currency = currency_obj.search(
                    [("name", "=", "INR"), ("active", "=", False)], limit=1
                )
                existing_currency.active = True

            if existing_currency:
                existing_currency.write(vals)
            else:
                vals["name"] = name
                vals["full_name"] = vals["bc_currency_code"]
                vals["decimal_places"] = vals["bc_decimal_places"]
                currency_obj.create(vals)

            imported_count += 1

        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message="Sucessfully fetched currencies",
            record_count=imported_count,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": _("Currencies Imported"),
                "message": _("Successfully imported %d currencies." % imported_count),
                "sticky": False,
            },
        }

    def action_export_customers_to_bigcommerce(self):
        fail = 0
        import math

        self.ensure_one()
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export customer.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Missing API credentials on the store record.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Missing API credentials."))

        customers = self.env["res.partner"].search(
            [("bigcommerce_customer_id", "=", 0)]
        )
        if not customers:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export customer.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No new customers to export.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("No new customers to export."))

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/customers"
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        def parse_datetime(dt_str):
            if not dt_str:
                return False
            if dt_str.endswith("Z"):
                dt_str = dt_str[:-1]
            dt_str = dt_str.replace("T", " ")
            return fields.Datetime.to_datetime(dt_str)

        batch_size = 10
        total = len(customers)
        batches = math.ceil(total / batch_size)

        for i in range(batches):
            batch_customers = customers[i * batch_size : (i + 1) * batch_size]
            payload = []
            for customer in batch_customers:
                customer_data = {
                    "email": customer.email or f"{customer.id}@example.com",
                    "first_name": customer.name.split()[0]
                    if customer.name
                    else "Unknown",
                    "last_name": customer.name.split()[-1]
                    if customer.name
                    else "Customer",
                    "company": customer.bigcommerce_company or "",
                    "phone": customer.phone or "",
                    "notes": customer.bigcommerce_notes or "",
                    "tax_exempt_category": customer.bigcommerce_tax_exempt_category
                    or "",
                    "customer_group_id": customer.bigcommerce_group_id or 0,
                    "addresses": [
                        {
                            "address1": customer.street
                            if customer.street
                            else "Unknown Street",
                            "city": customer.city if customer.city else "AHEMDABAD",
                            "country_code": customer.country_id.code
                            if customer.country_id
                            else "IN",
                            "first_name": customer.name.split()[0]
                            if customer.name
                            else "Unknown",
                            "last_name": customer.name.split()[-1]
                            if customer.name
                            else "Customer",
                            "phone": customer.phone if customer.phone else "1234567890",
                            "postal_code": customer.zip if customer.zip else "360001",
                            "state_or_province": customer.state_id.name
                            if customer.state_id
                            else "Gujarat",
                        }
                    ],
                    "accepts_product_review_abandoned_cart_emails": customer.bigcommerce_accepts_review_emails,
                    "origin_channel_id": customer.bigcommerce_origin_channel_id or 1,
                    "trigger_account_created_notification": True,
                }
                payload.append(customer_data)

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code not in [200, 201]:
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Unsucessfull to export customers.",
                    record_count=fail,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=f"Failed to export customers: {response.text}",
                    cr_user_id=self.env.uid,
                )
                raise UserError(_("Failed to export customers: %s") % response.text)

            data = response.json().get("data", [])
            for cust_data, partner in zip(data, batch_customers):
                partner.write(
                    {
                        "bigcommerce_store_id": self.id,
                        "bigcommerce_customer_id": cust_data.get("id"),
                        "bigcommerce_date_created": parse_datetime(
                            cust_data.get("date_created")
                        ),
                        "bigcommerce_date_modified": parse_datetime(
                            cust_data.get("date_modified")
                        ),
                        "bigcommerce_company": cust_data.get("company"),
                        "bigcommerce_group_id": cust_data.get("customer_group_id"),
                        "bigcommerce_notes": cust_data.get("notes"),
                    }
                )

        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message="Sucessfully exported customer",
            record_count=total,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Export Success"),
                "message": _(
                    f"Exported {total} customers to BigCommerce successfully."
                ),
                "type": "success",
                "sticky": False,
            },
        }

    def action_export_customer_addresses(self):
        self.ensure_one()
        count = 0
        fail = 0
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export customer address.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Missing API credentials for this BigCommerce store.",
                cr_user_id=self.env.uid,
            )
            raise UserError("Missing API credentials for this BigCommerce store.")

        # Get all customers linked to this store with BigCommerce customer IDs
        customers = self.env["res.partner"].search(
            [
                ("bigcommerce_store_id", "=", self.id),
                ("bigcommerce_customer_id", "!=", 0),
            ]
        )

        if not customers:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export customer address.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No customers with BigCommerce customer IDs found to export addresses.",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                "No customers with BigCommerce customer IDs found to export addresses."
            )

        # Prepare all addresses of these customers (assuming addresses stored in res.partner or res.partner.address)
        # Here, I assume customers have addresses stored in `child_ids` or some address model linked
        # Adjust as per your data model

        all_addresses = []
        for customer in customers:
            count += 1
            addresses = customer.child_ids.filtered(
                lambda a: a.type in ("contact", "delivery", "invoice")
            )  # or any logic to pick addresses
            for addr in addresses:
                first_name, last_name = payment_utils.split_partner_name(addr.name)
                address_data = {
                    "customer_id": customer.bigcommerce_customer_id,
                    "first_name": first_name or customer.name.split()[0]
                    if customer.name
                    else "Unknown",
                    "last_name": last_name or customer.name.split()[-1]
                    if customer.name
                    else "Customer",
                    "company": addr.company_id.name or customer.company_name or "",
                    "address1": addr.street or "Unknown Street",
                    "address2": addr.street2 or "",
                    "city": addr.city or "Unknown City",
                    "state_or_province": addr.state_id.name if addr.state_id else "",
                    "postal_code": addr.zip or "",
                    "country_code": addr.country_id.code if addr.country_id else "US",
                    "phone": addr.phone or customer.phone or "",
                    "address_type": "residential",  # or "commercial", add logic if needed
                    "form_fields": [],
                }
                all_addresses.append(address_data)

        if not all_addresses:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export customer address.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No addresses found for customers to export.",
                cr_user_id=self.env.uid,
            )
            raise UserError("No addresses found for customers to export.")

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/customers/addresses"
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        batch_size = 10
        total = len(all_addresses)
        batches = math.ceil(total / batch_size)

        for i in range(batches):
            batch = all_addresses[i * batch_size : (i + 1) * batch_size]
            response = requests.post(url, headers=headers, json=batch)
            if response.status_code not in [200, 201]:
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Unsucessfull to export customer address.",
                    record_count=fail,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=f"Failed to export addresses batch {i + 1}: {response.text}",
                    cr_user_id=self.env.uid,
                )
                raise UserError(
                    f"Failed to export addresses batch {i + 1}: {response.text}"
                )

        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message="Sucessfully export customer address.",
            record_count=count,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Export Success",
                "message": f"Exported {total} addresses to BigCommerce successfully.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_export_brands_to_bigcommerce(self):
        """ Export brands to BigCommerce via Create Brand API """
        count = 0
        fail = 0
        self.ensure_one()

        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export brand.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Missing BigCommerce API credentials.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Missing BigCommerce API credentials."))

        # Find brands to export (those without a brand_id yet)
        brands = self.env["bigcommerce.brand"].search(
            [("store_id", "=", self.id), ("brand_id", "=", False)]
        )

        if not brands:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export brand.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No brands to export.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("No brands to export."))

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/catalog/brands"
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        success = 0
        failed = 0

        for brand in brands:
            # Prepare payload, including optional fields only if they are valid
            payload = {"name": brand.name}

            if brand.page_title:
                payload["page_title"] = str(brand.page_title)

            if brand.meta_description:
                payload["meta_description"] = str(brand.meta_description)

            if brand.search_keywords:
                payload["search_keywords"] = str(brand.search_keywords)

            if brand.image_url:
                payload["image_url"] = str(brand.image_url)

            if brand.meta_keywords:
                payload["meta_keywords"] = [
                    kw.strip() for kw in brand.meta_keywords.split(",") if kw.strip()
                ]

            if brand.custom_url:
                payload["custom_url"] = {
                    "url": str(brand.custom_url),
                    "is_customized": bool(brand.is_customized_url),
                }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                data = response.json().get("data", {})
                brand.write({"brand_id": data.get("id")})
                success += 1
            else:
                failed += 1
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Unsucessfully export brand",
                    record_count=failed,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=f"Failed to export brand {brand.name} {response.text}",
                    cr_user_id=self.env.uid,
                )
                _logger.warning(
                    "Failed to export brand '%s': %s", brand.name, response.text
                )

        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message="Sucessfully export brand",
            record_count=success,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Export Completed"),
                "message": _("Exported %s brand(s). Failed: %s" % (success, failed)),
                "type": "success" if failed == 0 else "warning",
                "sticky": False,
            },
        }

    def action_export_categories_to_bigcommerce(self):
        """Export product categories to BigCommerce, ensuring parents are created before children."""
        self.ensure_one()
        count = 0
        fail = 0
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsuccessful to export categories.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="Missing BigCommerce API credentials.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Missing BigCommerce API credentials."))

        # Fetch categories without bigcommerce_category_id
        categories = self.env["product.category"].search(
            [("bigcommerce_category_id", "=", 0)]
        )

        if not categories:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsuccessful to export categories.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="No categories to export.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("No categories to export."))

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/catalog/trees/categories"
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url_for_tree = (
            f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/catalog/trees"
        )
        response = requests.get(url_for_tree, headers=headers)
        response_data = response.json()

        # Get the first tree ID
        tree_id = (
            response_data.get("data", [])[0].get("id")
            if response_data.get("data")
            else None
        )

        def get_category_level(category):
            """Calculate the hierarchy level of a category (0 for top-level, 1 for first-level child, etc.)."""
            level = 0
            current = category
            while current.parent_id:
                level += 1
                current = current.parent_id
            return level

        def build_payload(category):
            """Build payload for a category."""
            if not category.bigcommerce_tree_id:
                category.bigcommerce_tree_id = tree_id

            cat_payload = {"name": category.name}

            if not category.parent_id and category.bigcommerce_tree_id:
                cat_payload["tree_id"] = category.bigcommerce_tree_id
            elif category.parent_id and category.parent_id.bigcommerce_category_id:
                cat_payload["parent_id"] = category.parent_id.bigcommerce_category_id
            else:
                return None

            if category.page_title:
                cat_payload["page_title"] = category.page_title
            if category.search_keywords:
                cat_payload["search_keywords"] = category.search_keywords
            if category.layout_file:
                cat_payload["layout_file"] = category.layout_file
            if category.image_url:
                cat_payload["image_url"] = category.image_url
            if category.default_product_sort:
                cat_payload["default_product_sort"] = category.default_product_sort
            if category.sort_order is not None:
                cat_payload["sort_order"] = category.sort_order
            if category.views is not None:
                cat_payload["views"] = category.views

            cat_payload["is_visible"] = True

            if category.url_path:
                cat_payload["url"] = {
                    "path": category.url_path,
                    "is_customized": category.is_url_customized,
                }

            return cat_payload

        def process_response(response_data, category_batch):
            """Update Odoo categories with API response data."""
            nonlocal count
            for data in response_data:
                category = category_batch.filtered(lambda c: c.name == data.get("name"))
                if not category:
                    continue

                url_data = data.get("url", {})

                category.write(
                    {
                        "bigcommerce_store_id": self.id,
                        "bigcommerce_category_id": data.get("category_id"),
                        "bigcommerce_tree_id": data.get("tree_id"),
                        "bigcommerce_parent_id": data.get("parent_id"),
                        "page_title": data.get("page_title"),
                        "views": data.get("views"),
                        "sort_order": data.get("sort_order"),
                        "search_keywords": data.get("search_keywords"),
                        "layout_file": data.get("layout_file"),
                        "is_visible": data.get("is_visible"),
                        "default_product_sort": data.get("default_product_sort"),
                        "image_url": data.get("image_url"),
                        "url_path": url_data.get("path"),
                        "is_url_customized": url_data.get("is_customized"),
                    }
                )
                count += 1

        # Group categories by hierarchy level
        level_map = {}
        for category in categories:
            level = get_category_level(category)
            if level not in level_map:
                level_map[level] = self.env["product.category"]
            level_map[level] |= category

        # Process categories level by level
        for level in sorted(level_map.keys()):
            category_batch = level_map[level]
            payloads = []
            for category in category_batch:
                payload = build_payload(category)
                if payload:
                    payloads.append(payload)

            if not payloads:
                continue

            # Send API request for the batch
            response = requests.post(url, headers=headers, json=payloads)
            if response.status_code != 201:
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message=f"Unsuccessful to export categories at level {level}.",
                    record_count=fail,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=f"Failed to export categories at level {level}: {response.text}",
                    cr_user_id=self.env.uid,
                )
                raise UserError(
                    _("Failed to export categories at level %d. %s")
                    % (level, response.text)
                )

            response_data = response.json().get("data", [])
            process_response(response_data, category_batch)

        if count == 0:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsuccessful to export categories.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="No valid categories were exported.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("No valid categories were exported."))

        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message="Successfully exported categories",
            record_count=count,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Export Complete"),
                "message": _("Successfully exported %d categories to BigCommerce.")
                % count,
                "type": "success",
                "sticky": False,
            },
        }

    def upload_bigcommerce_product_image(self, product, store_hash, access_token):
        count = 0
        fail = 0
        if not product.image_1920:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message=f"No image found for export",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No image found for product: {product.name}",
                cr_user_id=self.env.uid,
            )
            _logger.warning("No image found for product: %s", product.name)
            return

        url = f"https://api.bigcommerce.com/stores/{store_hash}/v3/catalog/products/{product.bigcommerce_product_id}/images"

        headers = {
            "X-Auth-Token": access_token,
            "Accept": "application/json"
            # DO NOT set Content-Type manually here — requests will handle it
        }

        # Guess mimetype (default to image/jpeg)
        mimetype = mimetypes.guess_type("product_image.jpg")[0] or "image/jpeg"

        # Convert binary to file-like
        image_file = io.BytesIO(product.image_1920)

        # Named file — BigCommerce REQUIRES filename with extension
        files = {"image_file": ("product_image.jpg", image_file, mimetype)}

        # Optional: include description or thumbnail
        data = {"is_thumbnail": "true", "description": f"Main image for {product.name}"}

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code in [200, 201]:
            count += 1
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message=f"Image uploaded for product: {product.name}",
                record_count=count,
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
            )
        else:
            fail += 1
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export image",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to upload image for product :  {product.name} Status: {response.status_code}, Response: {response.text}",
                cr_user_id=self.env.uid,
            )
            _logger.error(
                "❌ Failed to upload image for product %s. Status: %s, Response: %s",
                product.name,
                response.status_code,
                response.text,
            )

    def action_export_products_to_bigcommerce(self):
        """Export products to BigCommerce and update fields from API response."""
        self.ensure_one()
        created_count = 0
        fail = 0

        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export product.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="Missing API credentials on the store record.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Missing BigCommerce API credentials."))

        products = self.env["product.template"].search(
            [("bigcommerce_product_id", "=", None), ("type", "=", "consu")]
        )

        if not products:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export products.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="No products to export.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("No products to export."))

        url = (
            f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/catalog/products"
        )
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        product_payloads = []
        product_map = {}

        for product in products:
            try:
                bigcommerce_cat_id = product.categ_id.bigcommerce_category_id
                product.bigcommerce_categories = bigcommerce_cat_id
                category_ids = [bigcommerce_cat_id] if bigcommerce_cat_id else []
            except Exception:
                continue

            tracking = "product" if not product.product_variant_ids else "variant"
            fallback_sku = product.default_code or f"tmpl-{product.id}"

            payload = {
                "bigcommerce_store_id": self.id,
                "name": product.name,
                "type": product.bigcommerce_type or "physical",
                "sku": fallback_sku,
                "description": product.bigcommerce_description or "",
                "weight": product.bigcommerce_weight or 0,
                "width": product.bigcommerce_width,
                "depth": product.bigcommerce_depth,
                "height": product.bigcommerce_height,
                "cost_price": product.bigcommerce_cost_price or 0,
                "price": product.list_price or product.bigcommerce_sale_price,
                "map_price": product.bigcommerce_map_price,
                "tax_class_id": product.bigcommerce_tax_class_id,
                "product_tax_code": product.bigcommerce_product_tax_code or "",
                "calculated_price": product.bigcommerce_calculated_price,
                "categories": category_ids,
                "brand_id": product.bigcommerce_brand_id.brand_id
                if product.bigcommerce_brand_id
                else None,
                "option_set_id": product.bigcommerce_option_set_id,
                "inventory_tracking": tracking,
                "layout_file": product.bigcommerce_layout_file or "",
                "upc": product.bigcommerce_upc or "",
                "mpn": product.bigcommerce_mpn or "",
                "gtin": product.bigcommerce_gtin or "",
                "is_visible": True,
                "availability": product.bigcommerce_availability or "available",
                "condition": product.bigcommerce_condition or "New",
                "page_title": product.bigcommerce_page_title or "",
                "meta_description": product.bigcommerce_meta_description or "",
            }

            payload = {k: v for k, v in payload.items() if v not in [None, ""]}
            product_payloads.append(payload)
            product_map[product.id] = product

        if not product_payloads:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export products.",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="No valid product data to export.",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("No valid product data to export."))

        for payload in product_payloads:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                res_data = response.json().get("data")
                if not res_data:
                    continue

                product_name = res_data.get("name")
                product_id = next(
                    (pid for pid, p in product_map.items() if p.name == product_name),
                    None,
                )
                product = product_map.get(product_id)

                if not product:
                    continue

                product.bigcommerce_product_id = res_data.get("id")
                product.bigcommerce_store_id = self.id

                if product:
                    product.export_bigcommerce_product_images()

                if product.attribute_line_ids:
                    for attribute_line in product.attribute_line_ids:
                        product.create_bigcommerce_product_option(
                            product, attribute_line.attribute_id
                        )

                    for variant in product.product_variant_ids:
                        product.export_bigcommerce_variant(product, variant)
                else:
                    # fetch variant and update product.product
                    variant_url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/catalog/products/{product.bigcommerce_product_id}/variants"
                    variant_response = requests.get(variant_url, headers=headers)
                    if variant_response.status_code == 200:
                        data_list = variant_response.json().get("data", [])
                        if data_list:
                            variant_data = data_list[0]
                            prod_var = self.env["product.product"].search(
                                [("product_tmpl_id", "=", product.id)], limit=1
                            )
                            if prod_var:
                                prod_var.write(
                                    {
                                        "bigcommerce_product_attribute_id": variant_data.get(
                                            "id"
                                        ),
                                        "bigcommerce_product_id": variant_data.get(
                                            "product_id"
                                        ),
                                        "bigcommerce_sku": variant_data.get("sku"),
                                        "bigcommerce_sku_id": variant_data.get("sku_id")
                                        or 0,
                                        "bigcommerce_store_id": self.id,
                                    }
                                )

                created_count += 1
            else:
                self.env["cr.data.processing.log"].sudo()._log_data_processing(
                    cr_shop_id=self.id,
                    cr_message="Unsucessfull to export product.",
                    record_count=fail,
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=f"Failed to export product: {payload.get('name')} Response : {response.text}",
                    cr_user_id=self.env.uid,
                )
                _logger.warning(
                    "Failed to export product: %s\nResponse: %s",
                    payload.get("name"),
                    response.text,
                )

        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message="Sucessfully exported product",
            record_count=created_count,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Export Complete"),
                "message": _("Successfully exported %d products to BigCommerce.")
                % created_count,
                "type": "success",
                "sticky": False,
            },
        }

    def parse_datetime(self, dt_str):
        """Helper to parse ISO 8601 datetime to Odoo datetime."""
        if dt_str:
            dt_str = dt_str.replace("T", " ").replace("Z", "")
            return fields.Datetime.to_datetime(dt_str)
        return False

    def action_import_inventory_locations(self):
        self.ensure_one()
        fail = 0
        success = 0
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to import locations",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Missing API credentials on the store record.",
                cr_user_id=self.env.uid,
            )

            raise UserError(_("Missing access token or store hash."))

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/inventory/locations"
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to import locations",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to fetch inventory locations : {response.text}",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                _("Failed to fetch inventory locations: %s") % response.text
            )

        data = response.json().get("data", [])
        created_count = 0

        InventoryLocation = self.env["stock.location"]
        for location in data:
            address = location.get("address", {})
            geo = address.get("geo_coordinates", {})

            existing = InventoryLocation.search(
                [
                    ("name", "=", location.get("label")),
                    ("bigcommerce_store_id", "=", self.id),
                ],
                limit=1,
            )

            parent = InventoryLocation.search([("name", "=", "WH")], limit=1)

            vals = {
                "name": location.get("label"),
                "bigcommerce_store_id": self.id,
                "bc_location_id": location["id"],
                "code": location.get("code"),
                "label": location.get("label"),
                "description": location.get("description"),
                "managed_by_external_source": location.get(
                    "managed_by_external_source"
                ),
                "type_id": location.get("type_id"),
                "enabled": location.get("enabled"),
                "operating_hours": location.get("operating_hours"),
                "time_zone": location.get("time_zone"),
                "created_at": self.parse_datetime(location.get("created_at")),
                "updated_at": self.parse_datetime(location.get("updated_at")),
                "address1": address.get("address1"),
                "address2": address.get("address2"),
                "city": address.get("city"),
                "state": address.get("state"),
                "zip": address.get("zip"),
                "phone": address.get("phone"),
                "country_code": address.get("country_code"),
                "latitude": geo.get("latitude"),
                "longitude": geo.get("longitude"),
                "storefront_visibility": location.get("storefront_visibility"),
                "usage": "internal",
                "location_id": parent.id,
            }

            if existing:
                existing.write(vals)
            else:
                InventoryLocation.create(vals)
                created_count += 1

        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message="Sucessfully fetched inventory",
            record_count=created_count,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import Complete"),
                "message": _(
                    "Successfully imported %d inventory location(s) from BigCommerce."
                )
                % created_count,
                "type": "success",
                "sticky": False,
            },
        }

    def action_export_locations_to_bigcommerce(self):
        self.ensure_one()
        fail = 0
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/inventory/locations"

        # Get stock.locations with no bc_location_id and related to this store
        locations = self.env["stock.location"].search(
            [("bc_location_id", "=", None)], limit=4
        )

        VALID_US_STATE_CODES = [
            "AL",
            "AK",
            "AS",
            "AZ",
            "AR",
            "AE",
            "AA",
            "AP",
            "CA",
            "CO",
            "CT",
            "DE",
            "DC",
            "FM",
            "FL",
            "GA",
            "GU",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MH",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "MP",
            "OH",
            "OK",
            "OR",
            "PW",
            "PA",
            "PR",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VI",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        ]

        # Define helper functions here
        def to_bool(val):
            return (
                bool(val)
                if isinstance(val, bool)
                else str(val).strip().lower() in ("1", "true", "yes")
            )

        def to_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return 0.0

        payload = []
        for loc in locations:
            location_data = {
                "code": loc.code or f"BC-LOCATION-{loc.id}",
                "label": loc.name or loc.bc_label,
                "description": loc.description or "",
                "managed_by_external_source": to_bool(loc.managed_by_external_source),
                "type_id": loc.type_id or "PHYSICAL",
                "enabled": loc.enabled or False,
                "operating_hours": loc.operating_hours or "",
                "time_zone": loc.time_zone or "Etc/UTC",
                "address": {
                    "address1": loc.address1 or "N/A",
                    "email": "no-reply@example.com",
                    "address2": loc.address2 or "",
                    "city": loc.city or "N/A",
                    "state": loc.state if loc.state in VALID_US_STATE_CODES else "CA",
                    "zip": loc.zip or "00000",
                    "phone": loc.phone or "",
                    "geo_coordinates": {
                        "latitude": loc.latitude or 0.00,
                        "longitude": loc.longitude or 0.00,
                    },
                    "country_code": loc.country_code or "US",
                },
                "storefront_visibility": to_bool(loc.storefront_visibility),
                "special_hours": [],
            }
            payload.append(location_data)

        if not payload:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export locations",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No inventory locations to export",
                cr_user_id=self.env.uid,
            )
            raise UserError(_("No inventory locations to export."))

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [200, 201]:
            # Optional: Parse response and update bc_location_id
            created_locations = response.json()
            for i, loc in enumerate(locations):
                if i < len(created_locations.get("data", [])):
                    loc.bc_location_id = created_locations["data"][i].get("id")

            self.action_import_inventory_locations()
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Sucessfully fetched locations",
                record_count=len(payload),
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Export Complete"),
                    "message": _("Successfully exported %d locations to BigCommerce.")
                    % len(payload),
                    "type": "success",
                    "sticky": False,
                },
            }

        else:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to export locations",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to fetch locations: {response.text}",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                _("Failed to export locations. Response: %s") % response.text
            )

    def action_import_shipping_zones(self):
        self.ensure_one()
        fail = 0
        headers = {"X-Auth-Token": self.access_token, "Accept": "application/json"}
        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2/shipping/zones"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to fetched shipping zones",
                record_count=fail,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to fetch shipping zones: {response.text}",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                _("Failed to fetch shipping zones. Status code: %s\nResponse: %s")
                % (response.status_code, response.text)
            )

        data = response.json()
        created = 0
        updated = 0
        method_created = 0
        method_updated = 0
        for zone in data:
            locations_list = zone["locations"]

            # Initialize an empty list to store the IDs
            location_ids = []

            # Iterate through each location dictionary in the list
            for location in locations_list:
                # Extract the 'id' from the current location dictionary
                location_id = location["id"]
                # Add the extracted ID to our list
                location_ids.append(location_id)

            # Print the list of location IDs
            location = self.env["stock.location"].search(
                [
                    ("bigcommerce_store_id", "=", self.id),
                    ("bc_location_id", "=", location_ids[0]),
                ]
            )
            zone_vals = {
                "name": zone["name"],
                "zone_id": zone["id"],
                "type": zone.get("type"),
                "country_iso2": zone.get("locations", [{}])[0].get("country_iso2"),
                "free_shipping_enabled": zone["free_shipping"]["enabled"],
                "free_shipping_minimum_sub_total": float(
                    zone["free_shipping"]["minimum_sub_total"]
                ),
                "exclude_fixed_shipping_products": zone["free_shipping"][
                    "exclude_fixed_shipping_products"
                ],
                "display_separately": zone["handling_fees"]["display_separately"],
                "fixed_surcharge": float(zone["handling_fees"]["fixed_surcharge"]),
                "enabled": zone["enabled"],
                "bigcommerce_store_id": self.id,
                "location_id": location.id or "",
            }

            existing = self.env["bigcommerce.shipping.zone"].search(
                [("zone_id", "=", zone["id"]), ("bigcommerce_store_id", "=", self.id)],
                limit=1,
            )

            if not existing:
                self.env["bigcommerce.shipping.zone"].create(zone_vals)
                created += 1
            else:
                existing.write(zone_vals)
                updated += 1

                # ✅ Fetch and store shipping methods
            methods_url = f'https://api.bigcommerce.com/stores/{self.store_hash}/v2/shipping/zones/{zone["id"]}/methods'
            method_response = requests.get(methods_url, headers=headers)
            if method_response.status_code == 200:
                methods_data = method_response.json()
                zone = self.env["bigcommerce.shipping.zone"].search(
                    [
                        ("zone_id", "=", zone["id"]),
                        ("bigcommerce_store_id", "=", self.id),
                    ],
                    limit=1,
                )
                for method in methods_data:
                    big_id = method["id"]
                    method_vals = {
                        "delivery_type": "bigcommerce",
                        "bc_method_id": method["id"],
                        "zone_id": zone.id,
                        "name": method["name"],
                        "type": method["type"],
                        "enabled": method.get("enabled", False),
                        "is_fallback": method.get("is_fallback", False),
                        "fixed_surcharge": float(
                            method.get("handling_fees", {}).get("fixed_surcharge", 0)
                        ),
                        "minimum_sub_total": float(
                            method.get("settings", {})
                            .get("carrier_options", {})
                            .get("minimum_sub_total", 0)
                        )
                        if method["type"] == "freeshipping"
                        else 0,
                        "rate": float(method.get("settings", {}).get("rate", 0))
                        if method["type"] == "perorder"
                        else 0,
                        "channel_ids_text": ",".join(
                            str(cid) for cid in method.get("channel_ids", [])
                        ),
                        "store_id": self.id,
                    }
                    method_exist = self.env["delivery.carrier"].search(
                        [
                            ("store_id", "=", self.id),
                            ("zone_id", "=", existing.id),
                            ("bc_method_id", "=", method["id"]),
                        ]
                    )
                    if method_exist:
                        self.env["delivery.carrier"].write(method_vals)
                        method_updated += 1
                    else:
                        name = method["name"]
                        cat = self.env["product.category"].search(
                            [("name", "=", "Deliveries"),
                             ("bigcommerce_store_id",'=',self.id)]
                        )
                        if not cat:
                            cat = self.env["product.category"].create(
                                {
                                    "name": "Deliveries",
                                    "bigcommerce_store_id": self.id
                                }
                            )
                        product = self.env["product.product"].create(
                            {
                                "name": f"{name} Product",
                                "categ_id": cat.id,
                                "type": "service",
                                "sale_ok": False,
                                "purchase_ok": False,
                                "list_price": 0.0,
                                "default_code": f"Delivery_bigcom{big_id}",
                            }
                        )
                        method_vals["product_id"] = product.id
                        self.env["delivery.carrier"].create(method_vals)
                        method_created += 1
        cr_message = (
                         "Shipping Zones: %d created, %d updated. "
                         "Shipping Methods: %d created, %d updated."
                     ) % (created, updated, method_created, method_updated)
        self.env["cr.data.processing.log"].sudo()._log_data_processing(
            cr_shop_id=self.id,
            cr_message=cr_message,
            record_count=created + updated,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            cr_user_id=self.env.uid,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import Complete"),
                "message": _("Shipping Zones: %d created, %d updated. "
                         "Shipping Methods: %d created, %d updated."
                     ) % (created, updated, method_created, method_updated),
                "type": "success",
                "sticky": False,
            },
        }

    def _get_webhook_destination(self):
        """Get the current server URL for webhook destination."""
        base_url = self.env["ir.config_parameter"].get_param("web.base.url", "")
        # base_url = config.get('web.base.url', False)
        if not base_url:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to get base url.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Web base URL is not configured in Odoo settings.",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                "Web base URL is not configured in Odoo settings. "
                "Please set 'web.base.url' in Settings > Technical > Parameters > System Parameters."
            )

        # Ensure the URL uses HTTPS and port 443
        parsed_url = urlparse(base_url)
        if parsed_url.scheme != "https":
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Webhook destination must use HTTPS.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Webhook destination must use HTTPS. Please configure 'web.base.url' with an HTTPS URL.",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                "Webhook destination must use HTTPS. Please configure 'web.base.url' with an HTTPS URL."
            )
        if parsed_url.port and parsed_url.port != 443:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Webhook destination must be served on port 443.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Webhook destination must be served on port 443. Please configure 'web.base.url' accordingly.",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                "Webhook destination must be served on port 443. Please configure 'web.base.url' accordingly."
            )

        return f"{base_url.rstrip('/')}/webhooks"

    def action_create_order_created_webhook(self):
        """Create a webhook for store/order/created event and store its data."""
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'order created webhook'.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"BigCommerce store configuration is missing or incomplete.",
                cr_user_id=self.env.uid,
            )
            raise UserError("BigCommerce store configuration is missing or incomplete.")

        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/order/created"
        )
        if webhook:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "Order created webhook already exist for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/hooks"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": self.access_token,
        }
        payload = {
            "scope": "store/order/created",
            "destination": self._get_webhook_destination(),
            "is_active": True,
            "headers": {},
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            webhook_data = response.json().get("data", {})

            # Store webhook data
            self.env["bigcommerce.webhook"].create(
                {
                    "bigcommerce_store_id": self.id,
                    "webhook_id": webhook_data.get("id"),
                    "scope": webhook_data.get("scope"),
                    "destination": webhook_data.get("destination"),
                    "is_active": webhook_data.get("is_active", True),
                    "created_at": webhook_data.get("created_at"),
                    "updated_at": webhook_data.get("updated_at"),
                }
            )

            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Sucessfully created 'Order created webhook'.",
                record_count=1,
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                cr_user_id=self.env.uid,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Order created webhook created and stored successfully.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except requests.exceptions.RequestException as e:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to created 'Order created webhook'.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to create order created webhook: {str(e)}",
                cr_user_id=self.env.uid,
            )
            raise UserError(f"Failed to create order created webhook: {str(e)}")

    def action_create_order_updated_webhook(self):
        """Create a webhook for store/order/updated event and store its data."""
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'order updated webhook'.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"BigCommerce store configuration is missing or incomplete.",
                cr_user_id=self.env.uid,
            )
            raise UserError("BigCommerce store configuration is missing or incomplete.")

        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/order/updated"
        )
        if webhook:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "Order updated webhook already exist for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/hooks"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": self.access_token,
        }
        payload = {
            "scope": "store/order/updated",
            "destination": self._get_webhook_destination(),
            "is_active": True,
            "headers": {},
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            webhook_data = response.json().get("data", {})

            # Store webhook data
            self.env["bigcommerce.webhook"].create(
                {
                    "bigcommerce_store_id": self.id,
                    "webhook_id": webhook_data.get("id"),
                    "scope": webhook_data.get("scope"),
                    "destination": webhook_data.get("destination"),
                    "is_active": webhook_data.get("is_active", True),
                    "created_at": webhook_data.get("created_at"),
                    "updated_at": webhook_data.get("updated_at"),
                }
            )

            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Sucessfully created 'Order updated webhook'.",
                record_count=1,
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                cr_user_id=self.env.uid,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Order updated webhook created and stored successfully.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except requests.exceptions.RequestException as e:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to created 'Order created webhook'.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to create order updated webhook: {str(e)}",
                cr_user_id=self.env.uid,
            )
            raise UserError(f"Failed to create order updated webhook: {str(e)}")

    def action_create_order_refunded_webhook(self):
        """Create a webhook for store/order/refunded/created event and store its data."""
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'order refunded webhook'.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"BigCommerce store configuration is missing or incomplete.",
                cr_user_id=self.env.uid,
            )
            raise UserError("BigCommerce store configuration is missing or incomplete.")

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/hooks"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": self.access_token,
        }
        payload = {
            "scope": "store/order/refunded/created",
            "destination": self._get_webhook_destination(),
            "is_active": True,
            "headers": {},
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            webhook_data = response.json().get("data", {})

            # Store webhook data
            self.env["bigcommerce.webhook"].create(
                {
                    "bigcommerce_store_id": self.id,
                    "webhook_id": webhook_data.get("id"),
                    "scope": webhook_data.get("scope"),
                    "destination": webhook_data.get("destination"),
                    "is_active": webhook_data.get("is_active", True),
                    "created_at": webhook_data.get("created_at"),
                    "updated_at": webhook_data.get("updated_at"),
                }
            )

            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Sucessfully created 'Order refunded webhook'.",
                record_count=1,
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                cr_user_id=self.env.uid,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Order refunded webhook created and stored successfully.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except requests.exceptions.RequestException as e:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to created 'Order refunded webhook'.",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to create order refunded webhook: {str(e)}",
                cr_user_id=self.env.uid,
            )
            raise UserError(f"Failed to create order refunded webhook: {str(e)}")

    def action_delete_order_created_webhook(self):
        """Delete the webhook for store/order/created event."""
        self.ensure_one()
        webhook = self.webhook_ids.filtered(lambda w: w.scope == "store/order/created")
        if not webhook:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to delete 'order created webhook'",
                record_count=1,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"'store/order/created' webhook not found",
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "No order created webhook found for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        # Assuming one webhook per scope; take the first one if multiple exist
        return self.action_delete_webhook(webhook[0].webhook_id)

    def action_delete_order_updated_webhook(self):
        """Delete the webhook for store/order/updated event."""
        self.ensure_one()
        webhook = self.webhook_ids.filtered(lambda w: w.scope == "store/order/updated")
        if not webhook:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to delete 'order update webhook'",
                record_count=1,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"'store/order/updated' webhook not found",
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "No order updated webhook found for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        # Assuming one webhook per scope; take the first one if multiple exist
        return self.action_delete_webhook(webhook[0].webhook_id)

    def action_delete_order_refunded_webhook(self):
        """Delete the webhook for store/order/refunded/created event."""
        self.ensure_one()
        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/order/refunded/created"
        )
        if not webhook:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to delete 'order refunded webhook'",
                record_count=1,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"'store/order/refunded/created' webhook not found",
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "No order refunded webhook found for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        # Assuming one webhook per scope; take the first one if multiple exist
        return self.action_delete_webhook(webhook[0].webhook_id)

    def action_delete_webhook(self, webhook_id):
        """Delete a webhook by its ID."""
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message=f"Fail to Delete {webhook_id}",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"BigCommerce store configuration is missing or incomplete.",
                cr_user_id=self.env.uid,
            )
            raise UserError("BigCommerce store configuration is missing or incomplete.")

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/hooks/{webhook_id}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": self.access_token,
        }

        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()

            # Remove webhook from Odoo
            webhook = self.env["bigcommerce.webhook"].search(
                [
                    ("bigcommerce_store_id", "=", self.id),
                    ("webhook_id", "=", webhook_id),
                ]
            )
            if webhook:
                webhook.unlink()

            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message=f"Webhook {webhook_id} deleted successfully.",
                record_count=1,
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": f"Webhook {webhook_id} deleted successfully.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except requests.exceptions.RequestException as e:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message=f"Unsucessfull to delete webhook {webhook_id}",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to delete webhook {webhook_id}: {str(e)}",
                cr_user_id=self.env.uid,
            )
            raise UserError(f"Failed to delete webhook {webhook_id}: {str(e)}")

    def action_create_product_created_webhook(self):
        """Create a webhook for store/product/created event and store its data."""
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'product created webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"BigCommerce store configuration is missing or incomplete.",
                cr_user_id=self.env.uid,
            )
            raise UserError("BigCommerce store configuration is missing or incomplete.")

        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/product/created"
        )
        if webhook:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "product created webhook already exist for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/hooks"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": self.access_token,
        }
        payload = {
            "scope": "store/product/created",
            "destination": self._get_webhook_destination(),
            "is_active": True,
            "headers": {},
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            webhook_data = response.json().get("data", {})

            # Store webhook data
            self.env["bigcommerce.webhook"].create(
                {
                    "bigcommerce_store_id": self.id,
                    "webhook_id": webhook_data.get("id"),
                    "scope": webhook_data.get("scope"),
                    "destination": webhook_data.get("destination"),
                    "is_active": webhook_data.get("is_active", True),
                    "created_at": webhook_data.get("created_at"),
                    "updated_at": webhook_data.get("updated_at"),
                }
            )

            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Sucessfully created 'product created webhook'",
                record_count=1,
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                cr_user_id=self.env.uid,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Product created webhook created and stored successfully.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except requests.exceptions.RequestException as e:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'product created webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to create product created webhook: {str(e)}",
                cr_user_id=self.env.uid,
            )
            raise UserError(f"Failed to create product created webhook: {str(e)}")

    def action_create_product_updated_webhook(self):
        """Create a webhook for store/product/updated event and store its data."""
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'product updated webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"BigCommerce store configuration is missing or incomplete.",
                cr_user_id=self.env.uid,
            )
            raise UserError("BigCommerce store configuration is missing or incomplete.")

        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/product/updated"
        )
        if webhook:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "product updated webhook already exist for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/hooks"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": self.access_token,
        }
        payload = {
            "scope": "store/product/updated",
            "destination": self._get_webhook_destination(),
            "is_active": True,
            "headers": {},
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            webhook_data = response.json().get("data", {})

            # Store webhook data
            self.env["bigcommerce.webhook"].create(
                {
                    "bigcommerce_store_id": self.id,
                    "webhook_id": webhook_data.get("id"),
                    "scope": webhook_data.get("scope"),
                    "destination": webhook_data.get("destination"),
                    "is_active": webhook_data.get("is_active", True),
                    "created_at": webhook_data.get("created_at"),
                    "updated_at": webhook_data.get("updated_at"),
                }
            )

            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Sucessfully created 'product updated webhook'",
                record_count=1,
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                cr_user_id=self.env.uid,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Product updated webhook created and stored successfully.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except requests.exceptions.RequestException as e:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'product updated webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to create product updated webhook: {str(e)}",
                cr_user_id=self.env.uid,
            )
            raise UserError(f"Failed to create product updated webhook: {str(e)}")

    def action_delete_product_created_webhook(self):
        """Delete the webhook for store/product/created event."""
        self.ensure_one()
        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/product/updated"
        )
        if not webhook:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to delete 'product updated webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No product updated webhook found for 'store/product/updated'",
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "No product updated webhook found for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/product/created"
        )
        if not webhook:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to delete 'product created webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No product created webhook found for 'store/product/created'",
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "No product created webhook found for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        # Assuming one webhook per scope; take the first one if multiple exist
        return self.action_delete_webhook(webhook[0].webhook_id)

    def action_delete_product_updated_webhook(self):
        """Delete the webhook for store/product/updated event."""
        self.ensure_one()
        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/product/updated"
        )
        if not webhook:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to delete 'product updated webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No product updated webhook found for 'store/product/updated'",
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "No product updated webhook found for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        # Assuming one webhook per scope; take the first one if multiple exist
        return self.action_delete_webhook(webhook[0].webhook_id)

    def action_create_product_inventory_updated_webhook(self):
        """Create a webhook for store/product/inventory/updated event and store its data."""
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'product inventory updated webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"BigCommerce store configuration is missing or incomplete.",
                cr_user_id=self.env.uid,
            )
            raise UserError("BigCommerce store configuration is missing or incomplete.")

        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/channel/*/inventory/product/stock_changed"
        )
        if webhook:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "Product inventory updated webhook already exist for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/hooks"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": str(self.access_token),
        }
        payload = {
            "scope": "store/channel/*/inventory/product/stock_changed",
            "destination": self._get_webhook_destination(),
            "is_active": True,
            "headers": {},
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            webhook_data = response.json().get("data", {})

            # Store webhook data
            self.env["bigcommerce.webhook"].sudo().create(
                {
                    "bigcommerce_store_id": self.id,
                    "webhook_id": webhook_data.get("id"),
                    "scope": webhook_data.get("scope"),
                    "destination": webhook_data.get("destination"),
                    "is_active": webhook_data.get("is_active", True),
                    "created_at": webhook_data.get("created_at"),
                    "updated_at": webhook_data.get("updated_at"),
                }
            )
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Sucessfully created 'product inventory updated webhook'",
                record_count=1,
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Product inventory updated webhook created and stored successfully.",
                    "type": "success",
                    "sticky": False,
                },
            }
        except requests.exceptions.RequestException as e:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to create 'product inventory updated webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Failed to create product inventory updated webhook: {str(e)}",
                cr_user_id=self.env.uid,
            )
            raise UserError(
                f"Failed to create product inventory updated webhook: {str(e)}"
            )

    def action_delete_product_inventory_updated_webhook(self):
        """Delete the webhook for store/product/inventory/updated event."""
        self.ensure_one()
        webhook = self.webhook_ids.filtered(
            lambda w: w.scope == "store/channel/*/inventory/product/stock_changed"
        )
        if not webhook:
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                cr_shop_id=self.id,
                cr_message="Unsucessfull to delete 'product inventory updated webhook'",
                record_count=0,
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"No product inventory updated webhook found for this store.",
                cr_user_id=self.env.uid,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Warning",
                    "message": "No product inventory updated webhook found for this store.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        return self.action_delete_webhook(webhook[0].webhook_id)


    def is_customer_exist(self, order_data):
        customer_query = """
                    SELECT * FROM res_partner
                    WHERE bigcommerce_customer_id = %s
                      AND bigcommerce_store_id = %s
                      AND (company_id = %s OR company_id IS NULL)
                """
        self.env.cr.execute(
            customer_query, (order_data["customer_id"], self.id, self.company_id.id)
        )
        columns = [col[0] for col in self.env.cr.description]
        result = self.env.cr.fetchall()

        # Combine column names with row values
        customer = {}
        for row in result:
            customer_dict = dict(zip(columns, row))
            customer = customer_dict

        if not result:
            if self.auto_create_customer:
                self.action_import_bigcommerce_customers()
                self.action_import_bigcommerce_customer_addresses()

                customer_query = """
                                    SELECT * FROM res_partner
                                    WHERE bigcommerce_customer_id = %s
                                      AND bigcommerce_store_id = %s
                                      AND (company_id = %s OR company_id IS NULL)
                                """
                self.env.cr.execute(
                    customer_query,
                    (order_data["customer_id"], self.id, self.company_id.id),
                )
                columns = [col[0] for col in self.env.cr.description]
                result = self.env.cr.fetchall()

                for row in result:
                    customer_dict = dict(zip(columns, row))
                    customer = customer_dict
            else:
                return "customer_not_found"

        return customer

    def get_product(self, prod):
        product_query = """
                           SELECT * FROM product_product
                           WHERE bigcommerce_product_id = %s
                             AND bigcommerce_product_attribute_id = %s
                             AND bigcommerce_store_id = %s
                       """
        self.env.cr.execute(
            product_query, (prod["product_id"], prod["variant_id"], self.id)
        )
        product_columns1 = [col[0] for col in self.env.cr.description]
        product_data = self.env.cr.fetchall()
        cr_product = {}
        for row in product_data:
            product_dict = dict(zip(product_columns1, row))
            cr_product = product_dict

        if not cr_product:
            product_query1 = f"""SELECT * FROM product_product WHERE bigcommerce_product_id = %s AND bigcommerce_store_id=%s"""
            self.env.cr.execute(product_query1, (prod["product_id"], self.id))
            product_columns2 = [col[0] for col in self.env.cr.description]
            product_data2 = self.env.cr.fetchall()
            for row in product_data2:
                product_dict2 = dict(zip(product_columns2, row))
                cr_product = product_dict2

        return cr_product

    def _process_bigcommerce_order(self, order_data, headers):
        """Process a single BigCommerce order for creation or update."""
        # Find customer
        customer = self.is_customer_exist(order_data)
        if customer == "customer_not_found":
            return "customer_not_found"

        # Get product lines
        products_url = order_data.get("products", {}).get("url")
        if not products_url:
            error_msg = f"No products URL for order {order_data['id']}"
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Failed to process order: No products URL",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            _logger.warning("No products URL for order %s, skipping", order_data["id"])
            return False

        try:
            prod_response = requests.get(products_url, headers=headers)
            prod_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_msg = (
                f"Failed to fetch products for order {order_data['id']}: {str(e)}"
            )
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Failed to process order: Product fetch error",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            _logger.error(
                "Failed to fetch products for order %s: %s", order_data["id"], str(e)
            )
            return False

        shipping_addresses = []
        shipping_addresses_data = order_data.get("shipping_addresses", {})
        if (
                isinstance(shipping_addresses_data, dict)
                and "url" in shipping_addresses_data
        ):
            try:
                addr_response = requests.get(
                    shipping_addresses_data["url"], headers=headers
                )
                addr_response.raise_for_status()
                shipping_addresses = addr_response.json()
            except requests.exceptions.RequestException as e:
                error_msg = f"Failed to fetch shipping addresses for order {order_data['id']}: {str(e)}"
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to process order: Shipping address fetch error",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                _logger.error(
                    "Failed to fetch shipping addresses for order %s: %s",
                    order_data["id"],
                    str(e),
                )

        order_lines = []
        for prod in prod_response.json():
            cr_product = self.get_product(prod)
            product = (
                self.env["product.product"].browse(cr_product.get("id"))
                if cr_product.get("id")
                else None
            )
            if not product:
                if self.auto_create_product:
                    self.import_single_bigcommerce_product(prod["product_id"])
                    self.action_sync_inventory()
                    cr_product2 = self.get_product(prod)
                    product = (
                        self.env["product.product"].browse(cr_product2.get("id"))
                        if cr_product2.get("id")
                        else None
                    )
                else:
                    return "product_not_found"

            if product:
                shipping = shipping_addresses[0] if shipping_addresses else {}
                country = self.env["res.country"].search([("code", "=", shipping.get("country_iso2"))], limit=1)
                state = self.env["res.country.state"].search([
                    ("code", "=", shipping.get("state")),
                    ("country_id", "=", country.id),
                ], limit=1)
                zip_code = shipping.get("zip")

                # Always try to match best tax
                id = prod["product_id"]
                url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/catalog/products/{id}"

                tax_class_id = 0
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    tax_class_id = data["data"]["tax_class_id"]
                else:
                    _logger.info(f"Failed to fetch product data: {response.status_code} , {response.text}")
                tax = self._get_applicable_tax(country.id, state.id, zip_code,tax_class_id)

                # taxes = product.taxes_id
                order_lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": prod["quantity"],
                            "price_unit": float(prod["base_price"]),
                            "tax_id": [(6, 0, [tax.id])] if tax else [(6, 0, [])],
                            "company_id": self.company_id.id,
                            "currency_id": self.company_id.currency_id.id,
                            "price_subtotal": float(prod["total_ex_tax"]),
                            "price_total": float(prod["total_inc_tax"]),
                        },
                    )
                )
            else:
                return False

        # Get shipping details
        shipping_cost = float(order_data.get("shipping_cost_ex_tax", 0))
        carrier = False
        location = False
        tracking_number = False
        shipped_items = []
        zone = False

        if shipping_addresses and len(shipping_addresses) > 0:
            shipping = shipping_addresses[0]
            location_id = shipping.get("location_id")
            if location_id:
                location_query = f"""SELECT * FROM stock_location WHERE bc_location_id = %s AND bigcommerce_store_id=%s AND company_id in %s"""
                self.env.cr.execute(
                    location_query, (location_id, self.id, (False, self.company_id.id))
                )
                location = self.env.cr.fetchall()
        else:
            _logger.info(
                "No shipping addresses for order %s, proceeding without zone or location",
                order_data["id"],
            )

        # Update status based on BigCommerce status
        bc_status = order_data.get("status")

        # For shipped orders, fetch shipment details
        if order_data.get("status") == "Shipped":
            shipment_url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2/orders/{order_data['id']}/shipments"
            try:
                shipment_response = requests.get(shipment_url, headers=headers)
                _logger.info(
                    "shipment_response %s for order %s",
                    shipment_response.status_code,
                    order_data["id"],
                )
                if shipment_response.status_code == 204:
                    _logger.info(
                        "No shipment data for order %s (204 No Content)",
                        order_data["id"],
                    )
                else:
                    shipment_response.raise_for_status()
                    if shipment_response.text:
                        try:
                            shipments = shipment_response.json()
                            if isinstance(shipments, list) and shipments:
                                shipment = shipments[0]
                                carrier = (
                                    self.env["delivery.carrier"]
                                    .sudo()
                                    .search(
                                        [
                                            ("delivery_type", "=", "bigcommerce"),
                                            ("store_id", "=", self.id),
                                            (
                                                "name",
                                                "ilike",
                                                shipment["shipping_method"],
                                            ),
                                        ],
                                        limit=1,
                                    )
                                )

                                if not carrier:
                                    carrier = (
                                        self.env["delivery.carrier"]
                                        .sudo()
                                        .search(
                                            [
                                                ("delivery_type", "=", "bigcommerce"),
                                                ("store_id", "=", self.id),
                                                (
                                                    "name",
                                                    "ilike",
                                                    shipment[
                                                        "shipping_provider_display_name"
                                                    ],
                                                ),
                                            ],
                                            limit=1,
                                        )
                                    )

                                tracking_number = shipment.get("tracking_number")
                                shipped_items = shipment.get("items", [])
                            else:
                                _logger.info(
                                    "No shipments found for order %s", order_data["id"]
                                )
                        except ValueError as e:
                            error_msg = f"Invalid JSON response for shipments of order {order_data['id']}: {str(e)}"
                            self.env["cr.data.processing.log"]._log_data_processing(
                                cr_shop_id=self.id,
                                record_count=1,
                                cr_message="Failed to process order: Invalid shipment JSON",
                                status="failure",
                                timespan=str(fields.Datetime.now()),
                                initiated_at=str(fields.Datetime.now()),
                                error_message=error_msg,
                                cr_user_id=self.env.uid,
                            )
                            _logger.error(
                                "Invalid JSON response for shipments of order %s: %s. Response text: %s",
                                order_data["id"],
                                str(e),
                                shipment_response.text,
                            )
                    else:
                        _logger.info(
                            "Empty response for shipments of order %s", order_data["id"]
                        )
            except requests.exceptions.RequestException as e:
                error_msg = (
                    f"Failed to fetch shipments for order {order_data['id']}: {str(e)}"
                )
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to process order: Shipment fetch error",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                _logger.error(error_msg)

        # Validate shipping cost against carrier settings
        final_shipping_cost = shipping_cost
        if carrier and shipping_cost > 0:
            subtotal = float(order_data.get("subtotal_ex_tax", 0))
            if carrier.use_discounted_sub_total:
                subtotal -= float(order_data.get("discount_amount", 0))
            if carrier.minimum_sub_total and subtotal < carrier.minimum_sub_total:
                _logger.warning(
                    "Order %s subtotal (%s) below minimum (%s), skipping shipping",
                    order_data["id"],
                    subtotal,
                    carrier.minimum_sub_total,
                )
                final_shipping_cost = 0
            else:
                final_shipping_cost += carrier.fixed_surcharge

        # Find status
        status_query = f"""SELECT * FROM bigcommerce_order_status WHERE bigcommerce_status_id = %s AND store_id=%s"""
        self.env.cr.execute(status_query, (order_data.get("status_id"), self.id))
        status_columns = [col[0] for col in self.env.cr.description]
        status_result = self.env.cr.fetchall()

        status_result_data = {}
        # Combine column names with row values
        for row in status_result:
            status_result_dict = dict(zip(status_columns, row))
            status_result_data = status_result_dict

        # Determine Odoo state
        odoo_state = (
            "sale"
            if order_data.get("status")
            in [
                "Awaiting Fulfillment",
                "Awaiting Shipment",
                "Awaiting Pickup",
                "Partially Shipped",
                "Shipped",
                "Completed",
                "Awaiting Payment",
            ]
            else "draft"
        )

        # Parse date
        try:
            date_order = datetime.strptime(
                order_data["date_created"], "%a, %d %b %Y %H:%M:%S %z"
            ).replace(tzinfo=None)
        except ValueError:
            date_order = fields.Datetime.now()
            _logger.warning(
                "Invalid date format for order %s, using current time", order_data["id"]
            )

        currency = order_data.get("currency_id", "")
        currency_id_query = f"""SELECT * FROM res_currency WHERE bc_currency_id = %s AND bigcommerce_store_id=%s"""
        self.env.cr.execute(currency_id_query, (currency, self.id))
        currency_id_columns = [col[0] for col in self.env.cr.description]
        currency_id = self.env.cr.fetchall()

        currency_data = {}
        # Combine column names with row values
        for row in currency_id:
            currency = dict(zip(currency_id_columns, row))
            currency_data = currency

        # Prepare sale order values
        sale_order_vals = {
            "partner_id": customer.get("id"),
            "date_order": date_order,
            "bigcommerce_store_id": self.id,
            "bigcommerce_order_id": order_data["id"],
            "bigcommerce_order_status_id": status_result_data.get("id")
            if status_result_data
            else False,
            "bigcommerce_subtotal_ex_tax": float(order_data.get("subtotal_ex_tax", 0)),
            "bigcommerce_subtotal_inc_tax": float(
                order_data.get("subtotal_inc_tax", 0)
            ),
            "bigcommerce_subtotal_tax": float(order_data.get("subtotal_tax", 0)),
            "bigcommerce_base_shipping_cost": float(
                order_data.get("base_shipping_cost", 0)
            ),
            "bigcommerce_shipping_cost_ex_tax": float(
                order_data.get("shipping_cost_ex_tax", 0)
            ),
            "bigcommerce_shipping_cost_inc_tax": float(
                order_data.get("shipping_cost_inc_tax", 0)
            ),
            "bigcommerce_total_ex_tax": float(order_data.get("total_ex_tax", 0)),
            "bigcommerce_total_inc_tax": float(order_data.get("total_inc_tax", 0)),
            "bigcommerce_total_tax": float(order_data.get("total_tax", 0)),
            "bigcommerce_payment_method": order_data.get("payment_method", ""),
            "bigcommerce_payment_status": order_data.get("payment_status", ""),
            "bigcommerce_refunded_amount": float(order_data.get("refunded_amount", 0)),
            "bigcommerce_discount_amount": float(order_data.get("discount_amount", 0)),
            "bigcommerce_customer_message": order_data.get("customer_message", ""),
            "bigcommerce_staff_notes": order_data.get("staff_notes", ""),
            "order_line": order_lines,
            # 'state': odoo_state,
            "carrier_id": carrier.id if carrier else False,
            "company_id": self.company_id.id,
            "currency_id": currency_data.get("id")
            if currency_data
            else self.company_id.currency_id.id,
            # fallback if not found
        }

        # Create sale order
        if self.order_sequence:
            use_seq = self.order_sequence
            sequence_code = use_seq
            sequence = (
                self.env["ir.sequence"]
                .sudo()
                .search([("code", "=", sequence_code)], limit=1)
            )
            if not sequence:
                sequence = self.env["ir.sequence"].create(
                    {
                        "name": f"Sequence for {sequence_code}",
                        "code": sequence_code,
                        "prefix": f"{sequence_code}/%(year)s/",
                        "padding": 5,
                        "number_increment": 1,
                    }
                )

            generated_sequence = sequence.next_by_id()
            if generated_sequence:
                sale_order_vals["name"] = generated_sequence
        sale_order = self.env["sale.order"].sudo().create(sale_order_vals)
        if odoo_state == "sale":
            sale_order.action_confirm()
            for data in sale_order.picking_ids:
                if data.state == "confirmed":
                    for move in data.move_ids_without_package:
                        valid_quants = move.product_id.stock_quant_ids.filtered(
                            lambda q: q.location_id.usage == "internal"
                            and q.location_id.bc_location_id
                        )
                        if valid_quants:
                            data.location_id = valid_quants[0].location_id
                            data.action_assign()
                        else:
                            self.action_sync_inventory()
                            valid_quants = move.product_id.stock_quant_ids.filtered(
                                lambda q: q.location_id.usage == "internal"
                                and q.location_id.bc_location_id
                            )
                            if valid_quants:
                                data.location_id = valid_quants[0].location_id
                                data.action_assign()

        log_message = f"Created sale order for BigCommerce order {order_data['id']}"

        # Log successful order creation/update
        self.env["cr.data.processing.log"]._log_data_processing(
            cr_shop_id=self.id,
            record_count=1,
            cr_message=log_message,
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            error_message="",
            cr_user_id=self.env.uid,
        )
        # Set delivery cost if applicable
        if carrier and final_shipping_cost > 0:
            if sale_order._set_delivery_cost(carrier, final_shipping_cost):
                _logger.info(
                    "Set delivery cost %s for order %s with carrier %s",
                    final_shipping_cost,
                    order_data["id"],
                    carrier.name,
                )
            else:
                error_msg = f"Failed to set delivery cost for order {order_data['id']}: No delivery product for carrier {carrier.name}"
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to set delivery cost",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                _logger.warning(error_msg)

        # Handle shipped orders
        if order_data.get("status") == "Shipped":
            picking = sale_order.picking_ids

            if picking:
                if location:
                    picking.location_id = location.id
                # if carrier:
                #     picking.carrier_id = carrier.id
                if tracking_number:
                    picking.carrier_tracking_ref = tracking_number
                if shipped_items:
                    for item in shipped_items:
                        product_data = (
                            self.env["product.product"]
                            .sudo()
                            .search(
                                [
                                    ("bigcommerce_product_id", "=", item["product_id"]),
                                    ("bigcommerce_store_id", "=", self.id),
                                ],
                                limit=1,
                            )
                        )

                        if product_data:
                            move = picking.move_ids_without_package.filtered(
                                lambda m: m.product_id.id == product_data.id
                            )
                            if move:
                                move.quantity = item["quantity"]
                else:
                    _logger.info(
                        "No shipped items for order %s, skipping picking validation",
                        order_data["id"],
                    )

                if shipped_items and any(
                    move.quantity > 0 for move in picking.move_ids_without_package
                ):
                    try:
                        for move in picking.move_ids_without_package:
                            if move.product_uom_qty == move.quantity_done:
                                move.quantity_done = move.product_uom_qty

                        for company in sale_order.picking_ids.mapped("company_id"):
                            if not company.has_received_warning_stock_sms:
                                company.sudo().write({'has_received_warning_stock_sms': True})

                        # Process each picking
                        for picking in sale_order.picking_ids:
                            if picking.state == "draft":
                                picking.action_confirm()

                            if picking.state == "confirmed":
                                picking.action_assign()

                            pre_validate_state = picking.state
                            result = picking.button_validate()

                            if isinstance(result, dict) and result.get("type") == "ir.actions.act_window":
                                _logger.warning(
                                    f"[BigCommerce] Wizard returned instead of direct validation for picking {picking.name}")
                            elif picking.state == "done":
                                _logger.info(
                                    f"[BigCommerce] Picking {picking.name} successfully moved to 'done' state.")
                            else:
                                _logger.warning(
                                    f"[BigCommerce] Picking {picking.name} did not reach 'done' state (Current: {picking.state})")

                        self.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=self.id,
                            record_count=1,
                            cr_message=log_message,
                            status="success",
                            timespan=str(fields.Datetime.now()),
                            initiated_at=str(fields.Datetime.now()),
                            error_message="",
                            cr_user_id=self.env.uid,
                        )
                    except Exception as e:
                        error_msg = f"Failed to validate delivery for order {order_data['id']}: {str(e)}"
                        self.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=self.id,
                            record_count=1,
                            cr_message="Failed to validate delivery",
                            status="failure",
                            timespan=str(fields.Datetime.now()),
                            initiated_at=str(fields.Datetime.now()),
                            error_message=error_msg,
                            cr_user_id=self.env.uid,
                        )
                        _logger.error(error_msg)
                else:
                    error_msg = f"No quantities reserved or set for delivery of order {order_data['id']}"
                    _logger.warning(error_msg)
                    self.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=self.id,
                        record_count=1,
                        cr_message="Failed to validate delivery: No quantities reserved",
                        status="failure",
                        timespan=str(fields.Datetime.now()),
                        initiated_at=str(fields.Datetime.now()),
                        error_message=error_msg,
                        cr_user_id=self.env.uid,
                    )
                    _logger.warning(error_msg)

        if (
            order_data.get("status") in ["Cancelled", "Declined"]
            and sale_order.state != "cancel"
        ):
            sale_order._action_cancel()

        if order_data.get("status") in ["Shipped", "Completed"]:
            for data in sale_order.picking_ids:
                for move in data.move_ids_without_package:
                    if move.product_uom_qty != move.quantity:
                        move.quantity = move.product_uom_qty
                if data.state != "done":
                    data.button_validate()

        return sale_order

    def _get_applicable_tax(self, country_id, state_id, zip_code, tax_class='0'):
        FiscalPosition = self.env['account.fiscal.position'].sudo()
        FiscalPositionPostal = self.env['account.fiscal.position.postal'].sudo()
        FiscalPositionTax = self.env['account.fiscal.position.tax'].sudo()

        def _get_tax_from_fp(fp):
            if not fp:
                return None

            tax_lines = FiscalPositionTax.search([
                ('position_id', '=', fp.id),
            ])

            taxes = tax_lines.mapped('tax_dest_id')

            taxes = taxes.filtered(
                lambda t: t.company_id.id == self.env.company.id and t.bigcommerce_store_id.id == self.id
            )
            target_taxes = taxes.filtered(lambda t: str(t.bigcommerce_tax_class_id or '0') == str(tax_class))

            if target_taxes:
                return target_taxes[0]
            elif taxes:
                return taxes[0]

            return None

        # Priority 1: Match via postal code
        postal_matches = FiscalPositionPostal.search([
            ("country_id", "=", country_id),
            ("postal_code", "=", zip_code),
        ])

        fpos_from_postal = postal_matches.mapped("fiscal_position_id").filtered(
            lambda fp: fp.bigcommerce_store_id.id == self.id and (
                    not fp.state_ids or state_id in fp.state_ids.ids
            )
        )

        if fpos_from_postal:
            tax = _get_tax_from_fp(fpos_from_postal[0])
            if tax:
                return tax

        # Priority 2: country + state
        fpos = FiscalPosition.search([
            ("country_id", "=", country_id),
            ("state_ids", "in", [state_id]),
            ("bigcommerce_store_id", "=", self.id),
            ("company_id", "=", self.env.company.id),
        ], limit=1)
        if fpos:
            _logger.info(f"[BigCommerce] Found fiscal position: {fpos.name}")
        tax = _get_tax_from_fp(fpos)
        if tax:
            return tax

        # Priority 3: country only
        fpos = FiscalPosition.search([
            ("country_id", "=", country_id),
            ("bigcommerce_store_id", "=", self.id),
            ("company_id", "=", self.env.company.id),
        ], limit=1)
        if fpos:
            _logger.info(f"[BigCommerce] Found fiscal position: {fpos.name}")
        tax = _get_tax_from_fp(fpos)
        if tax:
            return tax

        # Priority 4: fallback (no country)
        fpos = FiscalPosition.search([
            ("country_id", "=", False),
            ("bigcommerce_store_id", "=", self.id),
            ("company_id", "=", self.env.company.id),
        ])

        for fp in fpos:
            tax = _get_tax_from_fp(fp)
            if tax:
                return tax

        return None

    def import_single_bigcommerce_product(self, product_id):
        """Import a single product by its BigCommerce ID."""
        self.ensure_one()
        store = self

        headers = {
            "X-Auth-Token": store.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise UserError(
                _("Failed to fetch product. Response code: %s") % response.status_code
            )

        item = response.json().get("data")
        if not item:
            raise UserError(_("No product data found in BigCommerce response."))

        existing_product = self.env["product.template"].search(
            [("bigcommerce_product_id", "=", item.get("id"))], limit=1
        )
        if existing_product:
            return existing_product

        shop_all_category_id = (
            self.env["product.category"]
            .search(
                [
                    ("bigcommerce_store_id", "=", store.id),
                    ("name", "ilike", "shop all"),
                ],
                limit=1,
            )
            .id
        )

        category_ids = (
            self.env["product.category"]
            .search(
                [
                    ("bigcommerce_category_id", "in", item.get("categories", [])),
                    ("bigcommerce_store_id", "=", store.id),
                    ("id", "!=", shop_all_category_id),
                ]
            )
            .ids
        )

        brand_rec = self.env["bigcommerce.brand"].search(
            [("brand_id", "=", item.get("brand_id")), ("store_id", "=", store.id)],
            limit=1,
        )

        tax_class_id = str(item.get("tax_class_id"))
        tax = None
        if tax_class_id not in (None, "", "None"):
            tax = (
                self.env["account.tax"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_tax_class_id", "=", tax_class_id),
                        ("bigcommerce_store_id", "=", store.id),
                    ],
                    limit=1,
                )
            )

        product = self.env["product.template"].create(
            {
                "name": item.get("name"),
                "bigcommerce_store_id": store.id,
                "bigcommerce_product_id": item.get("id"),
                "default_code": item.get("sku"),
                "list_price": item.get("price"),
                "bigcommerce_type": item.get("type"),
                "bigcommerce_description": item.get("description"),
                "bigcommerce_weight": item.get("weight"),
                "bigcommerce_width": item.get("width"),
                "bigcommerce_depth": item.get("depth"),
                "bigcommerce_height": item.get("height"),
                "bigcommerce_cost_price": item.get("cost_price"),
                "bigcommerce_sale_price": item.get("sale_price"),
                "bigcommerce_map_price": item.get("map_price"),
                "bigcommerce_tax_class_id": item.get("tax_class_id"),
                "bigcommerce_product_tax_code": item.get("product_tax_code"),
                "bigcommerce_calculated_price": item.get("calculated_price"),
                "bigcommerce_categories": ",".join(
                    map(str, item.get("categories", []))
                ),
                "bigcommerce_brand_id": brand_rec.id,
                "bigcommerce_option_set_id": item.get("option_set_id"),
                "bigcommerce_inventory_level": item.get("inventory_level"),
                "bigcommerce_tracking": item.get("inventory_tracking"),
                "bigcommerce_total_sold": item.get("total_sold"),
                "bigcommerce_layout_file": item.get("layout_file"),
                "bigcommerce_upc": item.get("upc"),
                "bigcommerce_mpn": item.get("mpn"),
                "bigcommerce_gtin": item.get("gtin"),
                "bigcommerce_url": item.get("custom_url", {}).get("url"),
                "bigcommerce_is_visible": item.get("is_visible"),
                "bigcommerce_availability": item.get("availability"),
                "bigcommerce_condition": item.get("condition"),
                "bigcommerce_page_title": item.get("page_title"),
                "bigcommerce_meta_description": item.get("meta_description"),
                "bigcommerce_view_count": item.get("view_count"),
                "categ_id": category_ids[0] if category_ids else False,
                "company_id": store.company_id.id,
                "type": "consu",
                "is_storable": True,
                "taxes_id": [(6, 0, [tax.id])] if tax else [(6, 0, [])],
            }
        )

        product.import_product_image()
        product.import_bigcommerce_variants()
        return product

    def action_import_bigcommerce_orders(self):
        """Import orders from BigCommerce to Odoo with batch processing."""
        import time

        imported_count = 0
        missing_customers = []
        missing_products = []

        for store in self:
            start_time = time.time()

            if not store.access_token or not store.store_hash:
                error_msg = "Missing API credentials on the store record."
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message="Failed to import orders: Missing API credentials",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(error_msg)

            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            # Fetch all orders with pagination
            all_orders = []
            page = 1
            limit = 250  # Maximum allowed by BigCommerce

            base_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders"

            while True:
                try:
                    params = {"page": page, "limit": limit}
                    response = requests.get(base_url, headers=headers, params=params, timeout=30)

                    if response.status_code == 200:
                        orders = response.json()
                        if not orders or len(orders) == 0:
                            break
                        all_orders.extend(orders)

                        # If we got fewer orders than the limit, we're on the last page
                        if len(orders) < limit:
                            break

                        page += 1
                        time.sleep(0.1)
                    elif response.status_code == 429:
                        time.sleep(30)
                        continue
                    else:
                        break
                except requests.exceptions.RequestException as e:
                    error_msg = f"Failed to fetch orders: {str(e)}"
                    self.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message="Failed to import orders: API fetch error",
                        status="failure",
                        timespan=str(fields.Datetime.now()),
                        initiated_at=str(fields.Datetime.now()),
                        error_message=error_msg,
                        cr_user_id=self.env.uid,
                    )
                    raise UserError(error_msg)

            if not all_orders:
                continue

            # Filter out existing orders in batch
            order_ids = [str(o.get("id")) for o in all_orders if o.get("id")]

            if order_ids:
                query = """
                    SELECT bigcommerce_order_id
                    FROM sale_order
                    WHERE bigcommerce_order_id IN %s AND bigcommerce_store_id = %s
                """
                self.env.cr.execute(query, (tuple(order_ids), store.id))
                existing_order_ids = set(str(row[0]) for row in self.env.cr.fetchall())
            else:
                existing_order_ids = set()

            orders_to_create = [o for o in all_orders if str(o.get("id")) not in existing_order_ids]

            if not orders_to_create:
                continue

            # Process orders sequentially but efficiently
            for idx, order in enumerate(orders_to_create, 1):
                try:
                    result = store._process_bigcommerce_order(order, headers)

                    if result == "customer_not_found":
                        missing_customers.append(order["id"])
                    elif result == "product_not_found":
                        missing_products.append(order["id"])
                    elif result:
                        imported_count += 1

                    # Commit after every 10 orders to avoid session timeout
                    if idx % 10 == 0:
                        self.env.cr.commit()
                        _logger.info(f"Processed {idx}/{len(orders_to_create)} orders")

                except Exception as e:
                    _logger.error(f"Failed to process order {order['id']}: {str(e)}")
                    self.env.cr.rollback()
                    continue

            # Final commit
            self.env.cr.commit()

            total_elapsed = time.time() - start_time

            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=imported_count,
                cr_message=f"Successfully imported {imported_count} orders in {total_elapsed:.2f}s",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=self.env.uid,
            )

        if missing_customers or missing_products:
            message = ""
            if missing_customers:
                message += _("Customer(s) not found for order(s): %s\n") % ", ".join(
                    map(str, missing_customers)
                )
            if missing_products:
                message += _("Product(s) not found for order(s): %s") % ", ".join(
                    map(str, missing_products)
                )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "danger",
                    "title": _("Import Warning"),
                    "message": message.strip(),
                    "sticky": True,
                },
            }

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": _("Orders Imported"),
                "message": _(
                    "Successfully imported %d sale order(s)." % imported_count
                ),
                "sticky": False,
            },
        }


    def action_import_bigcommerce_orders_by_date(self, from_date=None, to_date=None):
        """Import BigCommerce orders within a date range."""
        imported_count = 0
        for store in self:
            if not store.access_token or not store.store_hash:
                error_msg = "Missing API credentials on the store record."
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=0,
                    cr_message="Failed to import orders: Missing API credentials",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=store.env.uid,
                )
                raise UserError(error_msg)

            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            base_url = (
                f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders"
            )
            params = {}

            if from_date:
                params["min_date_created"] = from_date.strftime("%Y-%m-%dT%H:%M:%S")
            if to_date:
                params["max_date_created"] = to_date.strftime("%Y-%m-%dT%H:%M:%S")

            try:
                response = requests.get(base_url, headers=headers, params=params)
                response.raise_for_status()
                # Check content before parsing JSON
                if not response.content:
                    raise UserError(
                        "No data returned from BigCommerce (empty response)."
                    )

            except requests.exceptions.RequestException as e:
                error_msg = f"Failed to fetch orders: {str(e)}"
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=0,
                    cr_message="Failed to import orders: API fetch error",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=store.env.uid,
                )
                raise UserError(error_msg)

            orders = response.json()

            for order in orders:
                store.env.cr.execute(
                    """
                    SELECT id FROM sale_order
                    WHERE bigcommerce_order_id = %s AND bigcommerce_store_id = %s
                """,
                    (order["id"], store.id),
                )
                data = store.env.cr.fetchall()
                if data:
                    continue

                if store._process_bigcommerce_order(order, headers):
                    imported_count += 1

            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=imported_count,
                cr_message=f"Imported {imported_count} order(s) from {from_date or 'beginning'} to {to_date or 'now'}",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=store.env.uid,
            )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": _("Orders Imported"),
                "message": _(
                    "Successfully imported %d sale order(s)." % imported_count
                ),
                "sticky": False,
            },
        }

    def _fetch_customer(self, customer_id, order_id):
        """Fetch customer by BigCommerce customer ID."""
        customer = (
            self.env["res.partner"]
            .sudo()
            .search([("bigcommerce_customer_id", "=", customer_id)], limit=1)
        )
        if not customer:
            error_msg = f"Customer {customer_id} not found for order {order_id}"
            _logger.warning(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Failed to fetch customer",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            _logger.warning(error_msg)
            return False
        # Log successful customer fetch
        self.env["cr.data.processing.log"]._log_data_processing(
            cr_shop_id=self.id,
            record_count=1,
            cr_message=f"Customer {customer_id} fetched successfully for order {order_id}",
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            error_message="",
            cr_user_id=self.env.uid,
        )
        return customer

    def _fetch_product_lines(self, products_url, headers, order_id):
        """Fetch and prepare product lines from BigCommerce products URL."""
        try:
            prod_response = requests.get(products_url, headers=headers)
            prod_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch products for order {order_id}: {str(e)}"
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Failed to fetch product lines",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            _logger.error(error_msg)
            return False

        order_lines = []
        for prod in prod_response.json():
            product = (
                self.env["product.product"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_product_id", "=", prod["product_id"]),
                        ("bigcommerce_product_attribute_id", "=", prod["variant_id"]),
                        ("bigcommerce_store_id",'=',self.id),
                    ],
                    limit=1,
                )
            )

            if not product:
                product = (
                    self.env["product.product"]
                    .sudo()
                    .search(
                        [("bigcommerce_product_id", "=", prod["product_id"]),("bigcommerce_store_id",'=',self.id)], limit=1
                    )
                )

            order_lines.append(
                {
                    "product_id": product.id,
                    "product_uom_qty": prod["quantity"],
                    "price_unit": float(prod["base_price"]),
                    "bigcommerce_product_id": prod["product_id"],
                    "bigcommerce_product_attribute_id": prod["variant_id"],
                }
            )

        if not order_lines:
            error_msg = f"No valid order lines for order {order_id}"
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Failed to fetch product lines: No valid order lines",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            _logger.warning(error_msg)
            return False

        # Log successful product lines fetch
        self.env["cr.data.processing.log"]._log_data_processing(
            cr_shop_id=self.id,
            record_count=len(order_lines),
            cr_message=f"Successfully fetched {len(order_lines)} product line(s) for order {order_id}",
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            error_message="",
            cr_user_id=self.env.uid,
        )
        return order_lines

    def _fetch_shipping_details(self, order_data, headers, order_id):
        """Fetch shipping details, including addresses, carrier, and shipment data."""
        shipping_addresses = []
        shipping_addresses_data = order_data.get("shipping_addresses", {})
        if (
            isinstance(shipping_addresses_data, dict)
            and "url" in shipping_addresses_data
        ):
            try:
                addr_response = requests.get(
                    shipping_addresses_data["url"], headers=headers
                )
                addr_response.raise_for_status()
                shipping_addresses = addr_response.json()
            except requests.exceptions.RequestException as e:
                error_msg = (
                    f"Failed to fetch shipping addresses for order {order_id}: {str(e)}"
                )
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to fetch shipping addresses",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                _logger.error(error_msg)

        shipping_cost = float(order_data.get("shipping_cost_ex_tax", 0))
        carrier = False
        location = False
        tracking_number = False
        shipped_items = []
        zone = False

        if shipping_addresses and len(shipping_addresses) > 0:
            shipping = shipping_addresses[0]
            zone = (
                self.env["bigcommerce.shipping.zone"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_store_id", "=", self.id),
                        ("country_iso2", "=", shipping.get("country_iso2")),
                    ],
                    limit=1,
                )
            )

            location_id = shipping.get("location_id")
            if location_id:
                location = (
                    self.env["stock.location"]
                    .sudo()
                    .search(
                        [
                            ("bigcommerce_store_id", "=", self.id),
                            ("bc_location_id", "=", str(location_id)),
                        ],
                        limit=1,
                    )
                )
        else:
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"No shipping addresses for order {order_id}, proceeding without zone or location",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=self.env.uid,
            )
            _logger.info(
                "No shipping addresses for order %s, proceeding without zone or location",
                order_id,
            )

        # For shipped orders, fetch shipment details
        if order_data.get("status") == "Shipped":
            shipment_url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2/orders/{order_id}/shipments"
            try:
                shipment_response = requests.get(shipment_url, headers=headers)
                _logger.info(
                    "shipment_response %s for order %s",
                    shipment_response.status_code,
                    order_id,
                )
                if shipment_response.status_code == 204:
                    self.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=self.id,
                        record_count=1,
                        cr_message=f"No shipment data for order {order_id} (204 No Content)",
                        status="success",
                        timespan=str(fields.Datetime.now()),
                        initiated_at=str(fields.Datetime.now()),
                        error_message="",
                        cr_user_id=self.env.uid,
                    )
                    _logger.info(
                        "No shipment data for order %s (204 No Content)", order_id
                    )
                else:
                    shipment_response.raise_for_status()
                    if shipment_response.text:
                        try:
                            shipments = shipment_response.json()
                            if isinstance(shipments, list) and shipments:
                                shipment = shipments[0]
                                carrier = (
                                    self.env["delivery.carrier"]
                                    .sudo()
                                    .search(
                                        [
                                            ("delivery_type", "=", "bigcommerce"),
                                            ("store_id", "=", self.id),
                                            (
                                                "name",
                                                "ilike",
                                                shipment["shipping_method"],
                                            ),
                                        ],
                                        limit=1,
                                    )
                                )
                                if not carrier:
                                    carrier = (
                                        self.env["delivery.carrier"]
                                        .sudo()
                                        .search(
                                            [
                                                ("delivery_type", "=", "bigcommerce"),
                                                ("store_id", "=", self.id),
                                                (
                                                    "name",
                                                    "ilike",
                                                    shipment[
                                                        "shipping_provider_display_name"
                                                    ],
                                                ),
                                            ],
                                            limit=1,
                                        )
                                    )

                                tracking_number = shipment.get("tracking_number")
                                shipped_items = shipment.get("items", [])
                            else:
                                self.env["cr.data.processing.log"]._log_data_processing(
                                    cr_shop_id=self.id,
                                    record_count=1,
                                    cr_message=f"No shipments found for order {order_id}",
                                    status="success",
                                    timespan=str(fields.Datetime.now()),
                                    initiated_at=str(fields.Datetime.now()),
                                    error_message="",
                                    cr_user_id=self.env.uid,
                                )
                                _logger.info(
                                    "No shipments found for order %s", order_id
                                )
                        except ValueError as e:
                            error_msg = f"Invalid JSON response for shipments of order {order_id}: {str(e)}"
                            self.env["cr.data.processing.log"]._log_data_processing(
                                cr_shop_id=self.id,
                                record_count=1,
                                cr_message="Failed to fetch shipment details: Invalid JSON",
                                status="failure",
                                timespan=str(fields.Datetime.now()),
                                initiated_at=str(fields.Datetime.now()),
                                error_message=error_msg,
                                cr_user_id=self.env.uid,
                            )
                            _logger.error(error_msg)
                    else:
                        self.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=self.id,
                            record_count=1,
                            cr_message=f"Empty response for shipments of order {order_id}",
                            status="success",
                            timespan=str(fields.Datetime.now()),
                            initiated_at=str(fields.Datetime.now()),
                            error_message="",
                            cr_user_id=self.env.uid,
                        )
                        _logger.info(
                            "Empty response for shipments of order %s", order_id
                        )
            except requests.exceptions.RequestException as e:
                error_msg = f"Failed to fetch shipments for order {order_id}: {str(e)}"
                _logger.error(error_msg)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to fetch shipment details",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=str(fields.Datetime.now()),
                    cr_user_id=self.env.uid,
                )
                _logger.error(error_msg)

        # Validate shipping cost
        final_shipping_cost = shipping_cost
        if carrier and shipping_cost > 0:
            subtotal = float(order_data.get("subtotal_ex_tax", 0))
            if carrier.use_discounted_sub_total:
                subtotal -= float(order_data.get("discount_amount", 0))
            if carrier.minimum_sub_total and subtotal < carrier.minimum_sub_total:
                _logger.warning(
                    "Order %s subtotal (%s) below minimum (%s), skipping shipping",
                    order_id,
                    subtotal,
                    carrier.minimum_sub_total,
                )
                final_shipping_cost = 0
            else:
                final_shipping_cost += carrier.fixed_surcharge

        if carrier:
            # Set tax on carrier product
            shipping_tax = (
                self.env["account.tax"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_tax_class_id", "=", "2"),  # Shipping tax class
                        ("company_id", "=", self.env.company.id),
                    ],
                    limit=1,
                )
            )
            if carrier.product_id and shipping_tax:
                carrier.product_id.taxes_id = [(6, 0, [shipping_tax.id])]

            # Log successful shipping details fetch
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Successfully fetched shipping details for order {order_id}",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=self.env.uid,
            )
        return {
            "shipping_addresses": shipping_addresses,
            "final_shipping_cost": final_shipping_cost,
            "carrier": carrier,
            "location": location,
            "tracking_number": tracking_number,
            "shipped_items": shipped_items,
            "zone": zone,
        }

    def _update_bigcommerce_order(self, order_data, headers, sale_order):
        """Update an existing BigCommerce order in Odoo."""
        order_id = order_data["id"]
        _logger.info(f"[BigCommerce] Updating order {order_id}...")

        # Fetch customer
        customer = self._fetch_customer(order_data["customer_id"], order_id)
        _logger.info(
            f"[BigCommerce] Customer fetched: {customer.display_name if customer else 'NOT FOUND'}"
        )
        if not customer:
            error_msg = (
                f"Customer {order_data['customer_id']} not found for order {order_id}"
            )
            _logger.error(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Failed to update order {order_id}: Customer not found",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            return False

        # Fetch product lines
        products_url = order_data.get("products", {}).get("url")
        _logger.info(f"[BigCommerce] Products URL: {products_url}")
        if not products_url:
            error_msg = f"No products URL for order {order_id}"
            _logger.warning(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Failed to update order {order_id}: No products URL",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            return False

        order_lines = self._fetch_product_lines(products_url, headers, order_id)
        _logger.info(
            f"[BigCommerce] Fetched {len(order_lines)} product lines for order {order_id}"
        )
        if not order_lines:
            error_msg = f"No valid order lines for order {order_id}"
            _logger.warning(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Failed to update order {order_id}: No valid order lines",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            return False

        # Fetch shipping details
        shipping_data = self._fetch_shipping_details(order_data, headers, order_id)
        final_shipping_cost = shipping_data["final_shipping_cost"]
        carrier = shipping_data["carrier"]
        location = shipping_data["location"]
        tracking_number = shipping_data["tracking_number"]
        shipped_items = shipping_data["shipped_items"]
        _logger.info(
            f"[BigCommerce] Shipping data for order {order_id}: cost={final_shipping_cost}, carrier={carrier.name if carrier else 'None'}, location={location.name if location else 'None'}, tracking={tracking_number}"
        )

        # Order status
        status = (
            self.env["bigcommerce.order.status"]
            .sudo()
            .search(
                [
                    ("bigcommerce_status_id", "=", order_data.get("status_id")),
                    ("store_id", "=", self.id),
                ],
                limit=1,
            )
        )
        _logger.info(
            f"[BigCommerce] Found order status: {status.name if status else 'None'}"
        )

        # Determine state
        odoo_state = (
            "sale"
            if order_data.get("status")
            in [
                "Awaiting Fulfillment",
                "Awaiting Shipment",
                "Awaiting Pickup",
                "Partially Shipped",
                "Shipped",
                "Completed",
                "Awaiting Payment",
            ]
            else "draft"
        )
        _logger.info(f"[BigCommerce] Determined Odoo sale order state: {odoo_state}")

        sale_order_vals = self._prepare_sale_order_vals(
            order_data, customer, status, odoo_state, carrier
        )

        # Write sale order
        try:
            sale_order.write(sale_order_vals)
            if odoo_state == "sale":
                sale_order.action_confirm()
                for data in sale_order.picking_ids:
                    if data.state == "confirmed":
                        for move in data.move_ids_without_package:
                            valid_quants = move.product_id.stock_quant_ids.filtered(
                                lambda q: q.location_id.usage == "internal"
                                          and q.location_id.bc_location_id
                            )
                            if valid_quants:
                                data.location_id = valid_quants[0].location_id
                                data.action_assign()
                            else:
                                self.action_sync_inventory()
                                valid_quants = move.product_id.stock_quant_ids.filtered(
                                    lambda q: q.location_id.usage == "internal"
                                              and q.location_id.bc_location_id
                                )
                                if valid_quants:
                                    data.location_id = valid_quants[0].location_id
                                    data.action_assign()
            _logger.info(
                f"[BigCommerce] Updated sale order for BigCommerce order {order_id}"
            )
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Updated sale order for BigCommerce order {order_id}",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=self.env.uid,
            )
        except Exception as e:
            error_msg = f"Failed to update sale order {order_id}: {str(e)}"
            _logger.error(f"[BigCommerce] {error_msg}")
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Failed to update order {order_id}: Update error",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            return False

        # Delivery cost
        if carrier and final_shipping_cost > 0:
            _logger.info(
                f"[BigCommerce] Trying to set delivery cost: {final_shipping_cost} with carrier {carrier.name}"
            )
            if sale_order._set_delivery_cost(carrier, final_shipping_cost):
                _logger.info(
                    f"[BigCommerce] Delivery cost set successfully for order {order_id}"
                )
            else:
                error_msg = f"Failed to set delivery cost for order {order_id}: Carrier {carrier.name} has no delivery product"
                _logger.warning(f"[BigCommerce] {error_msg}")

        # Shipped status
        if order_data.get("status") == "Shipped":
            _logger.info(f"[BigCommerce] Handling shipment for order {order_id}")
            picking = sale_order.picking_ids

            if picking:
                if location:
                    picking.location_id = location.id
                if carrier:
                    picking.carrier_id = carrier.id
                if tracking_number:
                    picking.carrier_tracking_ref = tracking_number
                if shipped_items:
                    for item in shipped_items:
                        product = (
                            self.env["product.product"]
                            .sudo()
                            .search(
                                [("bigcommerce_product_id", "=", item["product_id"]),
                                 ("bigcommerce_store_id", "=", self.id)],
                                limit=1,
                            )
                        )
                        if product:
                            move = picking.move_ids_without_package.filtered(
                                lambda m: m.product_id.id == product.id
                            )
                            if move:
                                move.quantity = item["quantity"]
                                _logger.info(
                                    f"[BigCommerce] Set quantity {item['quantity']} for move: {move.name}"
                                )
                else:
                    _logger.info(
                        f"[BigCommerce] No shipped items for order {order_id}, skipping validation"
                    )

                if shipped_items and any(
                    move.product_uom_qty > 0
                    for move in picking.move_ids_without_package
                ):
                    try:
                        for move in picking.move_ids_without_package:
                            if move.product_uom_qty != move.quantity:
                                move.quantity = move.product_uom_qty

                        for company in sale_order.picking_ids.mapped("company_id"):
                            if not company.has_received_warning_stock_sms:
                                company.sudo().write({'has_received_warning_stock_sms': True})
                                _logger.info(
                                    f"[BigCommerce] Set has_received_warning_stock_sms=True for company {company.name}")

                        # Process each picking
                        for picking in sale_order.picking_ids:
                            if picking.state == "draft":
                                picking.action_confirm()

                            if picking.state == "confirmed":
                                picking.action_assign()

                            pre_validate_state = picking.state
                            result = picking.button_validate()

                            if isinstance(result, dict) and result.get("type") == "ir.actions.act_window":
                                _logger.warning(
                                    f"[BigCommerce] Wizard returned instead of direct validation for picking {picking.name}")
                            elif picking.state == "done":
                                _logger.info(
                                    f"[BigCommerce] Picking {picking.name} successfully moved to 'done' state.")
                            else:
                                _logger.warning(
                                    f"[BigCommerce] Picking {picking.name} did not reach 'done' state (Current: {picking.state})")

                    except Exception as e:
                        _logger.error(
                            f"[BigCommerce] Failed to validate picking for order {order_id}: {str(e)}"
                        )
                else:
                    _logger.warning(
                        f"[BigCommerce] No reserved quantities for picking of order {order_id}"
                    )

        # Final state updates
        bc_status = order_data.get("status")
        if bc_status == "Cancelled" and sale_order.state != "cancel":
            sale_order._action_cancel()
            _logger.info(f"[BigCommerce] Order {order_id} cancelled in Odoo.")
        if (
            bc_status in ["Awaiting Fulfillment", "Awaiting Shipment"]
            and sale_order.state == "draft"
        ):
            sale_order.action_confirm()
            _logger.info(f"[BigCommerce] Order {order_id} confirmed in Odoo.")

        if order_data.get("status") in ["Shipped", "Completed"]:
            for picking in sale_order.picking_ids:
                if picking.state != "done":
                    picking.button_validate()
                    _logger.info(
                        f"[BigCommerce] Picking validated post-final status for order {order_id}"
                    )

        _logger.info(f"[BigCommerce] Finished updating order {order_id}")
        return sale_order


    def _sync_products(self):
        """Sync BigCommerce products to Odoo with tax classes."""
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        url = (
            f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/catalog/products"
        )
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            products = response.json()["data"]
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Fetched {len(products)} products for store {self.store_hash}",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=self.env.uid,
            )
        except requests.exceptions.RequestException as e:
            error_msg = (
                f"Failed to fetch products for store {self.store_hash}: {str(e)}"
            )
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Failed to fetch products",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            _logger.error(error_msg)
            raise UserError(_("Failed to fetch products: %s") % str(e))

        created_products = 0
        updated_products = 0
        for prod in products:
            product = (
                self.env["product.product"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_product_id", "=", prod["id"]),
                        ("bigcommerce_store_id", "=", self.id),
                    ],
                    limit=1,
                )
            )
            tax_class_id = str(prod.get("tax_class_id", "0"))
            taxes = (
                self.env["account.tax"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_tax_class_id", "=", tax_class_id),
                        ("bigcommerce_store_id", "=", self.id),
                        ("company_id", "=", self.env.company.id),
                    ]
                )
            )

            product_vals = {
                "name": prod["name"],
                "bigcommerce_product_id": prod["id"],
                "bigcommerce_product_attribute_id": prod.get("variant_id", "0"),
                "bigcommerce_store_id": self.id,
                "list_price": prod["price"],
                "taxes_id": [(6, 0, taxes.ids)] if taxes else [(6, 0, [])],
            }

            if product:
                product.write(product_vals)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message=f"Updated product {prod['id']} with tax class {tax_class_id} (store {self.store_hash})",
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message="",
                    cr_user_id=self.env.uid,
                )
                updated_products += 1
                _logger.info(
                    "Updated product %s with tax class %s (store %s)",
                    prod["id"],
                    tax_class_id,
                    self.store_hash,
                )
            else:
                product_vals["type"] = "product"
                product = self.env["product.product"].sudo().create(product_vals)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message=f"Created product {prod['id']} with tax class {tax_class_id} (store {self.store_hash})",
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message="",
                    cr_user_id=self.env.uid,
                )
                created_products += 1
                _logger.info(
                    "Created product %s with tax class %s (store %s)",
                    prod["id"],
                    tax_class_id,
                    self.store_hash,
                )

        # Log completion of product synchronization
        self.env["cr.data.processing.log"]._log_data_processing(
            cr_shop_id=self.id,
            record_count=len(products),
            cr_message=f"Completed product synchronization for store {self.store_hash}: processed {len(products)} products, created {created_products} new products, updated {updated_products} products",
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            error_message="",
            cr_user_id=self.env.uid,
        )
        return True

    def _sync_tax_zones_and_rates(self):
        """Sync BigCommerce tax zones and rates to Odoo fiscal positions."""
        import requests
        from collections import defaultdict

        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        zones_url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/tax/zones"
        try:
            response = requests.get(zones_url, headers=headers)
            response.raise_for_status()
            zones = response.json()["data"]
        except requests.exceptions.RequestException as e:
            raise UserError(_(f"Failed to fetch tax zones: {str(e)}"))

        rates_url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/tax/rates"
        try:
            rates_response = requests.get(rates_url, headers=headers)
            rates_response.raise_for_status()
            rates_data = rates_response.json()["data"]
        except requests.exceptions.RequestException as e:
            raise UserError(_(f"Failed to fetch tax rates: {str(e)}"))

        rates_by_zone = defaultdict(list)
        for rate in rates_data:
            rates_by_zone[rate["tax_zone_id"]].append(rate)

        skipped_zones = []
        created_positions = 0
        updated_positions = 0

        for zone in zones:
            zone_name = zone["name"]
            zone_id = zone["id"]

            locations = zone["shopper_target_settings"].get("locations", [])
            _logger.info(f"locations: {locations}")

            # --- Modification: Handle empty locations as global/default zone ---
            if not locations:
                _logger.info(f"[BigCommerce] Zone '{zone_name}' has no locations — treating as GLOBAL zone.")
                is_global = True
            else:
                is_global = all(
                    not loc.get("country_code") and not loc.get("subdivision_codes") and not loc.get("postal_codes")
                    for loc in locations
                )

            if is_global:
                _logger.info(f"[BigCommerce] Global zone detected for zone: {zone_name}")
                tax_mappings = []
                zone_rates = rates_by_zone.get(zone_id, [])

                for rate in zone_rates:
                    for class_rate in rate.get("class_rates", []):
                        tax_class_id = int(class_rate["tax_class_id"])
                        tax_rate = class_rate["rate"]

                        tax_class_name = "Default Tax Class"
                        if tax_class_id != 0:
                            tax_class_url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2/tax_classes/{tax_class_id}"
                            tax_class_response = requests.get(tax_class_url, headers=headers)
                            if tax_class_response.status_code == 200:
                                tax_class_data = tax_class_response.json()
                                tax_class_name = tax_class_data.get("name", f"Class {tax_class_id}")

                        tax_name = f"{self.name} - {zone_name} - {tax_class_name}"

                        tax = self.env["account.tax"].sudo().search([
                            ("name", "=", tax_name),
                            ("bigcommerce_tax_class_id", "=", tax_class_id),
                            ("bigcommerce_store_id", "=", self.id),
                            ("company_id", "=", self.env.company.id),
                        ], limit=1)

                        tax_group = self.env["account.tax.group"].search([
                            ("country_id", "=", self.company_id.country_id.id)
                        ], limit=1)
                        if not tax_group:
                            tax_group = self.env["account.tax.group"].create({
                                "name": self.company_id.country_id.name,
                                "country_id": self.company_id.country_id.id
                            })

                        if not tax:
                            tax = self.env["account.tax"].sudo().create({
                                "name": tax_name,
                                "type_tax_use": "sale",
                                "amount_type": "percent",
                                "amount": tax_rate,
                                "company_id": self.env.company.id,
                                "bigcommerce_tax_class_id": tax_class_id,
                                "bigcommerce_store_id": self.id,
                                "country_id": self.env.company.country_id.id,
                                "tax_group_id": tax_group.id,
                            })
                            _logger.info(f"[BigCommerce] Created tax: {tax.name}")
                        else:
                            tax.write({"amount": tax_rate})
                            _logger.info(f"[BigCommerce] Updated tax: {tax.name} with rate {tax_rate}")

                        tax_mappings.append({"tax_src_id": tax.id, "tax_dest_id": tax.id})

                fp_name = f"{zone_name} - Global"
                fiscal_position = self.env["account.fiscal.position"].sudo().search([
                    ("name", "=", fp_name),
                    ("bigcommerce_store_id", "=", self.id),
                    ("company_id", "=", self.env.company.id),
                ], limit=1)

                fp_vals = {
                    "name": fp_name,
                    "company_id": self.env.company.id,
                    "bigcommerce_zone_id": zone_id,
                    "bigcommerce_store_id": self.id,
                    "tax_ids": [(5, 0, 0)] + [(0, 0, mapping) for mapping in tax_mappings],
                    "country_id": False,
                    "state_ids": [(5, 0, 0)],
                }
                _logger.info(f"[BigCommerce] Fiscal Position Values for Global Zone: {fp_vals}")

                if not fiscal_position:
                    self.env["account.fiscal.position"].sudo().create(fp_vals)
                    created_positions += 1
                    _logger.info("[BigCommerce] Created Global fiscal position")
                else:
                    fiscal_position.write(fp_vals)
                    updated_positions += 1
                    _logger.info("[BigCommerce] Updated Global fiscal position")
                continue

            country_state_map = defaultdict(set)
            postal_entries = []
            for loc in locations:
                country_code = loc.get("country_code")
                subdivision_codes = loc.get("subdivision_codes", [])
                postal_codes = loc.get("postal_codes", [])

                country = self.env["res.country"].search([("code", "=", country_code)], limit=1)
                if not country:
                    continue

                states = self.env["res.country.state"].search([
                    ("code", "in", subdivision_codes),
                    ("country_id", "=", country.id)
                ])
                country_state_map[country.id].update(states.ids)

                for postal in postal_codes:
                    postal_entries.append({
                        "country_id": country.id,
                        "postal_code": postal
                    })

            for country_id, state_ids in country_state_map.items():
                tax_mappings = []
                zone_rates = rates_by_zone.get(zone_id, [])

                if not zone_rates:
                    for tax in self.env["account.tax"].sudo().search([
                        ("bigcommerce_tax_class_id", "in", ["0", "1", "2", "3"]),
                        ("bigcommerce_store_id", "=", self.id),
                        ("company_id", "=", self.env.company.id),
                    ]):
                        tax_mappings.append({"tax_src_id": tax.id, "tax_dest_id": tax.id})
                else:
                    for rate in zone_rates:
                        for class_rate in rate.get("class_rates", []):
                            tax_class_id = int(class_rate["tax_class_id"])
                            tax_rate = class_rate["rate"]

                            tax_class_name = "Default Tax Class"
                            if tax_class_id != 0:
                                tax_class_url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2/tax_classes/{tax_class_id}"
                                tax_class_response = requests.get(tax_class_url, headers=headers)
                                if tax_class_response.status_code == 200:
                                    tax_class_data = tax_class_response.json()
                                    tax_class_name = tax_class_data.get("name", f"Class {tax_class_id}")

                            tax_name = f"{self.name} - {zone_name} - {tax_class_name}"

                            tax = self.env["account.tax"].sudo().search([
                                ("name", "=", tax_name),
                                ("bigcommerce_tax_class_id", "=", tax_class_id),
                                ("bigcommerce_store_id", "=", self.id),
                                ("company_id", "=", self.env.company.id),
                            ], limit=1)

                            tax_group = self.env["account.tax.group"].search([
                                ("country_id", "=", self.company_id.country_id.id)
                            ], limit=1)
                            if not tax_group:
                                tax_group = self.env["account.tax.group"].create({
                                    "name": self.company_id.country_id.name,
                                    "country_id": self.company_id.country_id.id
                                })

                            if not tax:
                                tax = self.env["account.tax"].sudo().create({
                                    "name": tax_name,
                                    "type_tax_use": "sale",
                                    "amount_type": "percent",
                                    "amount": tax_rate,
                                    "company_id": self.env.company.id,
                                    "bigcommerce_tax_class_id": tax_class_id,
                                    "bigcommerce_store_id": self.id,
                                    "country_id": self.env.company.country_id.id,
                                    "tax_group_id": tax_group.id,
                                })
                            else:
                                tax.write({"amount": tax_rate})

                            tax_mappings.append({"tax_src_id": tax.id, "tax_dest_id": tax.id})

                country = self.env["res.country"].browse(country_id)
                fp_name = f"{zone_name} - {country.name}"

                fiscal_position = self.env["account.fiscal.position"].sudo().search([
                    ("name", "=", fp_name),
                    ("bigcommerce_store_id", "=", self.id),
                    ("company_id", "=", self.env.company.id),
                ], limit=1)

                fp_vals = {
                    "name": fp_name,
                    "company_id": self.env.company.id,
                    "bigcommerce_zone_id": zone_id,
                    "bigcommerce_store_id": self.id,
                    "tax_ids": [(5, 0, 0)] + [(0, 0, mapping) for mapping in tax_mappings],
                    "country_id": country_id,
                    "state_ids": [(6, 0, list(state_ids))] if state_ids else [(5, 0, 0)],
                }

                if not fiscal_position:
                    fiscal_position = self.env["account.fiscal.position"].sudo().create(fp_vals)
                    created_positions += 1
                else:
                    fiscal_position.write(fp_vals)
                    updated_positions += 1

                for entry in postal_entries:
                    if entry["country_id"] == country_id:
                        self.env["account.fiscal.position.postal"].sudo().create({
                            "country_id": entry["country_id"],
                            "postal_code": entry["postal_code"],
                            "fiscal_position_id": fiscal_position.id,
                        })

        return {
            "success": True,
            "skipped_zones": skipped_zones,
            "created": created_positions,
            "updated": updated_positions,
        }


    def _prepare_sale_order_vals(
        self, order_data, customer, status, odoo_state, carrier
    ):
        """Prepare common sale order values."""
        try:
            date_order = datetime.strptime(
                order_data["date_created"], "%a, %d %b %Y %H:%M:%S %z"
            ).replace(tzinfo=None)
        except ValueError:
            date_order = fields.Datetime.now()
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Invalid date format for order {order_data['id']}, using current time",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=f"Invalid date format for order {order_data['id']}",
                cr_user_id=self.env.uid,
            )
            _logger.warning(
                "Invalid date format for order %s, using current time", order_data["id"]
            )

        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        # shipping_addresses = order_data.get('shipping_addresses', [{}])[0]
        shipping_addresses_data = order_data.get("shipping_addresses", {})
        if (
            isinstance(shipping_addresses_data, dict)
            and "url" in shipping_addresses_data
        ):
            try:
                addr_response = requests.get(
                    shipping_addresses_data["url"], headers=headers
                )
                addr_response.raise_for_status()
                shipping_addresses = addr_response.json()
            except requests.exceptions.RequestException as e:
                order_id = order_data["id"]
                error_msg = (
                    f"Failed to fetch shipping addresses for order {order_id}: {str(e)}"
                )
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to fetch shipping addresses",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                _logger.error(error_msg)

        sale_order_vals = {
            "partner_id": customer.id,
            "date_order": date_order,
            "bigcommerce_store_id": self.id,
            "bigcommerce_order_id": order_data["id"],
            "bigcommerce_order_status_id": status.id if status else False,
            "bigcommerce_subtotal_ex_tax": float(order_data.get("subtotal_ex_tax", 0)),
            "bigcommerce_subtotal_inc_tax": float(
                order_data.get("subtotal_inc_tax", 0)
            ),
            "bigcommerce_subtotal_tax": float(order_data.get("subtotal_tax", 0)),
            "bigcommerce_base_shipping_cost": float(
                order_data.get("base_shipping_cost", 0)
            ),
            "bigcommerce_shipping_cost_ex_tax": float(
                order_data.get("shipping_cost_ex_tax", 0)
            ),
            "bigcommerce_shipping_cost_inc_tax": float(
                order_data.get("shipping_cost_inc_tax", 0)
            ),
            "bigcommerce_total_ex_tax": float(order_data.get("total_ex_tax", 0)),
            "bigcommerce_total_inc_tax": float(order_data.get("total_inc_tax", 0)),
            "bigcommerce_total_tax": float(order_data.get("total_tax", 0)),
            "bigcommerce_payment_method": order_data.get("payment_method", ""),
            "bigcommerce_payment_status": order_data.get("payment_status", ""),
            "bigcommerce_refunded_amount": float(order_data.get("refunded_amount", 0)),
            "bigcommerce_discount_amount": float(order_data.get("discount_amount", 0)),
            "bigcommerce_customer_message": order_data.get("customer_message", ""),
            "bigcommerce_staff_notes": order_data.get("staff_notes", ""),
            "state": odoo_state,
            "carrier_id": carrier.id if carrier else False,
        }

        # Log successful preparation of sale order values
        self.env["cr.data.processing.log"]._log_data_processing(
            cr_shop_id=self.id,
            record_count=1,
            cr_message=f"Prepared sale order values for order {order_data['id']} (store {self.store_hash})",
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            error_message="",
            cr_user_id=self.env.uid,
        )

        return sale_order_vals

    def action_sync_taxes(self):
        """Sync BigCommerce taxes and products to Odoo with one button click."""
        self.ensure_one()
        try:
            # Sync tax zones and rates
            zone_result = self._sync_tax_zones_and_rates()
            if not zone_result["success"]:
                error_msg = (
                    f"Failed to sync tax zones and rates for store {self.store_hash}"
                )
                _logger.error(error_msg)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to sync tax zones and rates",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(
                    _("Failed to sync tax zones and rates for store %s.")
                    % self.store_hash
                )
            skipped_zones = zone_result["skipped_zones"]
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Synced tax zones and rates for store {self.store_hash}, skipped {len(skipped_zones)} zones",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=""
                if not skipped_zones
                else f"Skipped zones: {', '.join(skipped_zones)}",
                cr_user_id=self.env.uid,
            )

            # Prepare notification message
            message = (
                _("Taxes synced successfully for store %s.")
                % self.store_hash
            )
            if skipped_zones:
                message += _(" Skipped zones due to missing rates: %s.") % ", ".join(
                    skipped_zones
                )

            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Completed tax and product synchronization for store {self.store_hash}: {message}",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=""
                if not skipped_zones
                else f"Skipped zones: {', '.join(skipped_zones)}",
                cr_user_id=self.env.uid,
            )
            _logger.info(message)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": message,
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            error_msg = f"Error syncing taxes and products for store {self.store_hash}: {str(e)}"
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Error syncing taxes and products",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            _logger.error(error_msg)
            raise UserError(_("Error syncing taxes and products: %s") % str(e))

    def create_cron_jobs(self):
        """Creates cron jobs based on the configuration defined in the settings."""
        try:
            # Validate import_cron_value
            if not self.import_cron_value:
                error_msg = "Missing import cron value for store %s" % self.store_hash
                _logger.error(error_msg)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to create cron job: Missing import cron value",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(_("Please Enter Value In 'Import Cron Value'"))

            # Validate import_scheduled_units
            if not self.import_scheduled_units:
                error_msg = (
                    "Missing import scheduled units for store %s" % self.store_hash
                )
                _logger.error(error_msg)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to create cron job: Missing import scheduled units",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(_("Please Enter Value In 'Import Cron Units'"))

            # Create cron job
            self._create_cron(
                name="BigCommerce Product Import",
                model="bigcommerce.store",
                method_name="model.import_bigcommerce_products()",
                cron_unit=self.import_scheduled_units,
                cron_value=self.import_cron_value,
            )

            # Log successful cron job creation
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Created scheduled action for product import for store {self.store_hash}",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=self.env.uid,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Successful"),
                    "message": _("Created scheduled action for product import"),
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            error_msg = f"Error creating cron job for store {self.store_hash}: {str(e)}"
            _logger.error(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Error creating cron job for product import",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Error creating cron job: %s") % str(e))

    def create_order_cron(self):
        """Creates cron job for BigCommerce order import based on configuration."""
        try:
            # Validate import_cron_value1
            if not self.import_cron_value1:
                error_msg = (
                    "Missing import cron value for orders for store %s"
                    % self.store_hash
                )
                _logger.error(error_msg)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to create order import cron job: Missing import cron value",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(_("Please Enter Value In 'Import Cron Value'"))

            # Validate import_scheduled_units1
            if not self.import_scheduled_units1:
                error_msg = (
                    "Missing import scheduled units for orders for store %s"
                    % self.store_hash
                )
                _logger.error(error_msg)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message="Failed to create order import cron job: Missing import scheduled units",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(_("Please Enter Value In 'Import Cron Units'"))

            # Create cron job
            self._create_cron(
                name="BigCommerce Order Import",
                model="bigcommerce.store",
                method_name="model.action_import_bigcommerce_orders()",
                cron_unit=self.import_scheduled_units1,
                cron_value=self.import_cron_value1,
            )

            # Log successful cron job creation
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Created scheduled action for order import for store {self.store_hash}",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=self.env.uid,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Successful"),
                    "message": _("Created scheduled action for Order Import"),
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            error_msg = f"Error creating order import cron job for store {self.store_hash}: {str(e)}"
            _logger.error(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Error creating order import cron job",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Error creating cron job: %s") % str(e))

    def _create_cron(self, name, model, method_name, cron_unit, cron_value):
        """Helper method to create or update a cron job with nextcall."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            current_time = datetime.now()
            interval_timedelta = timedelta(**{f"{cron_unit}": cron_value})
            nextcall = current_time + interval_timedelta

            # Validate model
            model_id = (
                self.env["ir.model"].sudo().search([("model", "=", model)], limit=1).id
            )
            if not model_id:
                error_msg = f"Model {model} not found for cron job {name} (store {self.store_hash})"
                _logger.error(error_msg)
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message=f"Failed to create/update cron job {name}: Model not found",
                    status="failure",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message=error_msg,
                    cr_user_id=self.env.uid,
                )
                raise UserError(_("Model %s not found") % model)

            existing_cron = (
                self.env["ir.cron"].sudo().search([("name", "=", name)], limit=1)
            )
            if existing_cron:
                existing_cron.write(
                    {
                        "interval_number": cron_value,
                        "interval_type": cron_unit,
                        "model_id": model_id,
                        "code": f"{method_name}",
                        "nextcall": nextcall,
                    }
                )
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message=f"Updated cron job {name} for store {self.store_hash}",
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message="",
                    cr_user_id=self.env.uid,
                )
            else:
                self.env["ir.cron"].sudo().create(
                    {
                        "name": name,
                        "interval_number": cron_value,
                        "interval_type": cron_unit,
                        "model_id": model_id,
                        "code": f"{method_name}",
                        "nextcall": nextcall,
                        "active": True,
                    }
                )
                self.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=self.id,
                    record_count=1,
                    cr_message=f"Created cron job {name} for store {self.store_hash}",
                    status="success",
                    timespan=str(fields.Datetime.now()),
                    initiated_at=str(fields.Datetime.now()),
                    error_message="",
                    cr_user_id=self.env.uid,
                )

        except Exception as e:
            error_msg = f"Error creating/updating cron job {name} for store {self.store_hash}: {str(e)}"
            _logger.error(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Error creating/updating cron job {name}",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Error creating cron job: %s") % str(e))

    def action_sync_inventory(self):
        """Sync BigCommerce inventory to Odoo stock.quant."""
        self.ensure_one()
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            headers = {
                "X-Auth-Token": self.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3/inventory/items"
            # Fetch first page
            response = requests.get(
                url, headers=headers, params={"limit": 1000, "page": 1}
            )
            response.raise_for_status()
            data = response.json()
            items = data["data"]
            pagination = data["meta"]["pagination"]
            total_pages = pagination["total_pages"]

            # Handle pagination
            for page in range(2, total_pages + 1):
                response = requests.get(
                    url, headers=headers, params={"limit": 1000, "page": page}
                )
                response.raise_for_status()
                items.extend(response.json()["data"])

            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Fetched {len(items)} inventory items across {total_pages} pages for store {self.store_hash}",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message="",
                cr_user_id=self.env.uid,
            )

        except requests.exceptions.RequestException as e:
            error_msg = (
                f"Failed to fetch inventory for store {self.store_hash}: {str(e)}"
            )
            _logger.error(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Failed to fetch inventory items",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Failed to fetch inventory: %s") % str(e))

        skipped_items = []
        created_quants = 0
        updated_quants = 0
        try:
            for item in items:
                identity = item["identity"]
                product = (
                    self.env["product.product"]
                    .sudo()
                    .search(
                        [
                            ("bigcommerce_product_id", "=", identity["product_id"]),
                            (
                                "bigcommerce_product_attribute_id",
                                "=",
                                identity["variant_id"],
                            ),
                            ("bigcommerce_store_id", "=", self.id),
                        ],
                        limit=1,
                    )
                )
                if not product:
                    product1 = (
                        self.env["product.product"]
                        .sudo()
                        .search(
                            [("bigcommerce_product_id", "=", identity["product_id"]),("bigcommerce_store_id", "=", self.id),],
                            limit=1,
                        )
                    )
                    product = product1
                    if not product1:
                        _logger.warning(
                            "No product found for product_id %s, variant_id %s (store %s), SKU %s",
                            identity["product_id"],
                            identity["variant_id"],
                            self.store_hash,
                            identity["sku"],
                        )
                        self.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=self.id,
                            record_count=1,
                            cr_message=f"Skipped product for SKU {identity['sku']}: No product found (store {self.store_hash})",
                            status="success",
                            timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            initiated_at=initiated_at,
                            error_message=f"No product found for product_id {identity['product_id']}, variant_id {identity['variant_id']}",
                            cr_user_id=self.env.uid,
                        )
                        skipped_items.append(identity["sku"])
                        continue

                for location in item["locations"]:
                    if not (
                        location["location_enabled"]
                        and location["settings"]["is_in_stock"]
                    ):
                        _logger.info(
                            "Skipping disabled or out-of-stock location %s for SKU %s (store %s)",
                            location["location_id"],
                            identity["sku"],
                            self.store_hash,
                        )
                        self.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=self.id,
                            record_count=1,
                            cr_message=f"Skipped location {location['location_id']} for SKU {identity['sku']}: Disabled or out-of-stock (store {self.store_hash})",
                            status="success",
                            timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            initiated_at=initiated_at,
                            error_message=f"Location {location['location_code']} disabled or out-of-stock",
                            cr_user_id=self.env.uid,
                        )
                        continue

                    stock_location = (
                        self.env["stock.location"]
                        .sudo()
                        .search(
                            [
                                ("bc_location_id", "=", str(location["location_id"])),
                                ("bigcommerce_store_id", "=", self.id),
                            ],
                            limit=1,
                        )
                    )
                    if not stock_location:
                        _logger.warning(
                            "No stock location found for location_id %s (store %s), SKU %s",
                            location["location_id"],
                            self.store_hash,
                            identity["sku"],
                        )
                        self.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=self.id,
                            record_count=1,
                            cr_message=f"Skipped stock for SKU {identity['sku']} at location {location['location_code']}: No stock location found (store {self.store_hash})",
                            status="success",
                            timespan=str(fields.Datetime.now()),
                            initiated_at=str(fields.Datetime.now()),
                            error_message=f"No stock location found for location_id {location['location_id']}",
                            cr_user_id=self.env.uid,
                        )
                        skipped_items.append(
                            f"{identity['sku']} at location {location['location_code']}"
                        )
                        continue

                    # Update stock.quant
                    quant = (
                        self.env["stock.quant"]
                        .sudo()
                        .search(
                            [
                                ("product_id", "=", product.id),
                                ("location_id", "=", stock_location.id),
                            ],
                            limit=1,
                        )
                    )

                    # quantity = location['available_to_sell'] - location['settings']['safety_stock']
                    quantity = location["total_inventory_onhand"]
                    if quantity < 0:
                        quantity = 0

                    if quant:
                        quant.with_context(inventory_mode=True).write(
                            {
                                "quantity": quantity,
                                "inventory_date": fields.Datetime.now(),
                            }
                        )
                        _logger.info(
                            "Updated stock for SKU %s at location %s: %s units (store %s)",
                            identity["sku"],
                            location["location_code"],
                            quantity,
                            self.store_hash,
                        )
                        self.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=self.id,
                            record_count=1,
                            cr_message=f"Updated stock for SKU {identity['sku']} at location {location['location_code']}: {quantity} units (store {self.store_hash})",
                            status="success",
                            timespan=str(fields.Datetime.now()),
                            initiated_at=str(fields.Datetime.now()),
                            error_message="",
                            cr_user_id=self.env.uid,
                        )
                        updated_quants += 1
                    else:
                        self.env["stock.quant"].with_context(
                            inventory_mode=True
                        ).create(
                            {
                                "product_id": product.id,
                                "location_id": stock_location.id,
                                "quantity": quantity,
                                "inventory_date": fields.Datetime.now(),
                            }
                        )
                        _logger.info(
                            "Created stock for SKU %s at location %s: %s units (store %s)",
                            identity["sku"],
                            location["location_code"],
                            quantity,
                            self.store_hash,
                        )
                        self.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=self.id,
                            record_count=1,
                            cr_message=f"Created stock for SKU {identity['sku']} at location {location['location_code']}: {quantity} units (store {self.store_hash})",
                            status="success",
                            timespan=str(fields.Datetime.now()),
                            initiated_at=str(fields.Datetime.now()),
                            error_message="",
                            cr_user_id=self.env.uid,
                        )
                        created_quants += 1

            # Prepare notification message
            message = _("Inventory synced successfully for store %s.") % self.store_hash
            if skipped_items:
                message += _(" Skipped items/locations: %s.") % ", ".join(skipped_items)

            _logger.info(message)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message=f"Completed inventory synchronization for store {self.store_hash}: processed {len(items)} items, created {created_quants} stock entries, updated {updated_quants} stock entries, skipped {len(skipped_items)} items/locations",
                status="success",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=""
                if not skipped_items
                else f"Skipped items/locations: {', '.join(skipped_items)}",
                cr_user_id=self.env.uid,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": message,
                    "type": "success",
                    "sticky": False,
                },
            }

        except Exception as e:
            error_msg = f"Error syncing inventory for store {self.store_hash}: {str(e)}"
            _logger.error(error_msg)
            self.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=self.id,
                record_count=1,
                cr_message="Error syncing inventory",
                status="failure",
                timespan=str(fields.Datetime.now()),
                initiated_at=str(fields.Datetime.now()),
                error_message=error_msg,
                cr_user_id=self.env.uid,
            )
            raise UserError(_("Error syncing inventory: %s") % str(e))

    def bulk_export_inventory(self):
        products = self.env["product.product"].search(
            [("type", "=", "consu")], limit=50
        )
        count = products.action_export_inventory_to_bigcommerce(self)

        self.env["cr.data.processing.log"]._log_data_processing(
            cr_shop_id=self.id,
            record_count=count,
            cr_message="Successfully Export Stock to Bigcommerce",
            status="success",
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            error_message="",
            cr_user_id=self.env.uid,
        )

    def update_product_cron(self):
        """Update scheduled action for product import."""
        self.ensure_one()
        return self._create_cron(
            name="BigCommerce Product Import",
            model="bigcommerce.store",
            method_name="model.import_bigcommerce_products()",
            cron_unit=self.import_scheduled_units,
            cron_value=self.import_cron_value,
        )

    def delete_product_cron(self):
        """Delete product import cron job."""
        self.ensure_one()
        cron = (
            self.env["ir.cron"]
            .sudo()
            .search([("name", "=", "BigCommerce Product Import")], limit=1)
        )
        if cron:
            cron.unlink()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Deleted"),
                    "message": _("Product import scheduled action deleted."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        else:
            raise UserError(_("Product import scheduled action not found."))

    def update_order_cron(self):
        """Update scheduled action for order import."""
        self.ensure_one()
        return self._create_cron(
            name="BigCommerce Order Import",
            model="bigcommerce.store",
            method_name="model.action_import_bigcommerce_orders()",
            cron_unit=self.import_scheduled_units1,
            cron_value=self.import_cron_value1,
        )

    def delete_order_cron(self):
        """Delete order import cron job."""
        self.ensure_one()
        cron = (
            self.env["ir.cron"]
            .sudo()
            .search([("name", "=", "BigCommerce Order Import")], limit=1)
        )
        if cron:
            cron.unlink()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Deleted"),
                    "message": _("Order import scheduled action deleted."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        else:
            raise UserError(_("Order import scheduled action not found."))

    def action_open_logs_for_store(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Processing Logs",
            "res_model": "cr.data.processing.log",
            "view_mode": "list,form",
            "target": "current",
            "domain": [("cr_shop_id", "=", self.id)],
            "context": {"default_cr_shop_id": self.id},
        }

    def action_open_customers_for_store(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Customers",
            "res_model": "res.partner",
            "view_mode": "list,form",
            "target": "current",
            "domain": [("bigcommerce_store_id", "=", self.id)],
            "context": {"default_store_id": self.id},
        }

    def action_open_orders_for_store(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Orders",
            "res_model": "sale.order",
            "view_mode": "list,form",
            "target": "current",
            "domain": [("bigcommerce_store_id", "=", self.id)],
            "context": {"default_bigcommerce_store_id": self.id},
        }

    def action_open_products_for_store(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Products",
            "res_model": "product.template",
            "view_mode": "list,form",
            "target": "current",
            "domain": [("bigcommerce_store_id", "=", self.id)],
            "context": {"default_bigcommerce_store_id": self.id},
        }

    def action_open_shipped_orders_for_store(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Shipped Orders",
            "res_model": "stock.picking",
            "view_mode": "list,form",
            "target": "current",
            "domain": [("state", "=", "done")],
            "context": {"default_bigcommerce_store_id": self.id},
        }

    def action_open_refunded_orders_for_store(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Refunded Orders",
            "res_model": "sale.order",
            "view_mode": "list,form",
            "target": "current",
        }
