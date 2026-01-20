# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import json
import requests
import logging
from odoo import http
from odoo.exceptions import ValidationError
from odoo import http, fields, _
from datetime import datetime
from odoo.http import request

_logger = logging.getLogger(__name__)


class BigCommerceWebhookController(http.Controller):
    @http.route("/webhooks", type="json", auth="public", methods=["POST"], csrf=False)
    def handle_webhook(self):
        """Handle incoming webhooks from BigCommerce."""
        _logger.info("Received BigCommerce webhook request")
        try:
            # Parse JSON payload
            raw_data = request.httprequest.data.decode("UTF-8")
            payload = json.loads(raw_data)

            # Validate payload
            if not payload or "scope" not in payload or "data" not in payload:
                _logger.error("Invalid webhook payload: %s", raw_data)
                return {"status": "error", "message": "Invalid payload"}

            scope = payload["scope"]
            producer = payload.get("producer", "")
            store_hash = (
                producer.split("/")[-1] if producer and "/" in producer else None
            )
            if not store_hash:
                _logger.error("No store_hash found in producer: %s", producer)
                return {"status": "error", "message": "Store hash not found"}

            webhook_data = payload.get("data", {})

            # Find BigCommerce store
            store = (
                request.env["bigcommerce.store"]
                .sudo()
                .search([("store_hash", "=", store_hash)], limit=1)
            )
            if not store:
                _logger.error(
                    "No BigCommerce store found for store_hash: %s", store_hash
                )
                return {"status": "error", "message": "Store not found"}

            # Prepare headers for API calls
            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            # Process webhook based on scope
            if scope == "store/order/created":
                return self._process_order_webhook(
                    store, webhook_data, headers, is_update=False
                )
            elif scope == "store/order/updated":
                result = self._process_order_webhook(
                    store, webhook_data, headers, is_update=True
                )
                return result
            elif scope == "store/order/refunded/created":
                return self._process_order_refunded(store, webhook_data)
            elif scope == "store/product/created":
                return self._process_product_created(store, webhook_data)
            elif scope == "store/product/updated":
                return self._process_product_updated(store, webhook_data)
            elif scope == "store/product/inventory/updated":
                return self._process_product_inventory_updated(store, webhook_data)
            elif scope == "store/sku/inventory/updated":
                return self._process_sku_inventory_updated(store, webhook_data)
            else:
                _logger.warning("Unsupported webhook scope: %s", scope)
                return {"status": "error", "message": "Unsupported scope"}

        except json.JSONDecodeError as e:
            _logger.error("Invalid JSON in webhook payload: %s", str(e))
            return {"status": "error", "message": "Invalid JSON payload"}
        except Exception as e:
            _logger.exception("Error processing webhook: %s", str(e))
            return {"status": "error", "message": f"Error processing webhook: {str(e)}"}

    def _process_order_webhook(self, store, webhook_data, headers, is_update=False):
        """Process order creation or update webhook by fetching full order data."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        order_id = webhook_data.get("id")
        if not order_id:
            error_msg = f"No order ID in webhook data for store {store.store_hash}: {webhook_data}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process order webhook: No order ID provided",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            return {"status": "error", "message": "No order ID provided"}

        # Fetch full order data from BigCommerce API
        order_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order_id}"
        try:
            response = requests.get(order_url, headers=headers)
            response.raise_for_status()
            order_data = response.json()
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched order {order_id} data for store {store.store_hash}",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch order {order_id} for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Failed to fetch order {order_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            return {"status": "error", "message": f"Failed to fetch order: {str(e)}"}

        # Process order
        try:
            if is_update:
                sale_order = (
                    store.env["sale.order"]
                    .sudo()
                    .search([("bigcommerce_order_id", "=", order_id),("bigcommerce_store_id", "=", store.id)], limit=1)
                )
                if not sale_order:
                    _logger.info(
                        "Order %s not found for update, treating as creation", order_id
                    )
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Order {order_id} not found for update, treating as creation (store {store.store_hash})",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )
                    # sale_order = store._process_bigcommerce_order(order_data, headers)
                else:
                    sale_order = store._update_bigcommerce_order(
                        order_data, headers, sale_order
                    )

            else:
                group = request.env.ref("base.group_user")
                users = request.env["res.users"].sudo().search([])

                for user in users:
                    if group in user.groups_id:
                        partner_id = user.partner_id
                    else:
                        _logger.info(
                            f"User {user.name} is NOT in the Internal User group"
                        )

                result = store._process_bigcommerce_order(order_data, headers)
                if isinstance(result, str) and result == "customer_not_found":
                    error_msg = f"Customer not found for order {order_id} in store {store.store_hash}"
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Order {order_id} skipped: customer not found",
                        status="failure",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message=error_msg,
                        cr_user_id=request.uid,
                    )
                    user._notification_channel(
                        type="danger",
                        title="Customer Missing",
                        message=f"Order {order_id} skipped: customer not found",
                        sticky=True,
                        target=partner_id,
                    )

                elif isinstance(result, str) and result == "product_not_found":
                    error_msg = f"Product not found for order {order_id} in store {store.store_hash}"
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Order {order_id} skipped: product not found",
                        status="failure",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message=error_msg,
                        cr_user_id=request.uid,
                    )
                    # return ('product_not_found', error_msg)
                    user._notification_channel(
                        type="danger",
                        title="Product Missing",
                        message=f"Product not found for order {order_id}.",
                        sticky=True,
                        target=partner_id,
                    )

                else:
                    sale_order = result
                    user._notification_channel(
                        type="info",
                        title="Order Created",
                        message=f"Order {sale_order.id} created sucessfully.",
                        sticky=True,
                        target=partner_id,
                    )

        except Exception as e:
            error_msg = f"Error processing order webhook {order_id} for store {store.store_hash}: {str(e)}"
            _logger.exception(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing order webhook {order_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            return {"status": "error", "message": f"Error processing order: {str(e)}"}

    def _process_order_refunded(self, store, data):
        """Process store/order/refunded/created webhook: Create a refund in Odoo."""
        order_id = data.get("order_id")
        refund_data = data.get("refund", {})
        if not order_id or not refund_data:
            raise ValidationError("Order ID or refund data missing in webhook data")

        # Find existing order
        order = (
            request.env["sale.order"]
            .sudo()
            .search(
                [
                    ("bigcommerce_store_id", "=", store.id),
                    ("bigcommerce_order_id", "=", str(order_id)),
                ],
                limit=1,
            )
        )
        if not order:
            _logger.warning("Order %s not found in Odoo for refund", order_id)
            return

        # Check if refund already processed
        refund_amount = float(refund_data.get("amount", 0.0))
        existing_refunded = (
            request.env["account.move"]
            .sudo()
            .search(
                [
                    ("sale_order_id", "=", order.id),
                    ("move_type", "=", "out_refunded"),
                    ("amount_total", "=", refund_amount),
                ],
                limit=1,
            )
        )
        if existing_refunded:
            _logger.info("Refund already processed for order %s", order_id)
            return

        # Create credit note (refund)
        refund_vals = {
            "move_type": "out_refunded",
            "partner_id": order.partner_id.id,
            "sale_order_id": order.id,
            "amount_total": refund_amount,
            "invoice_date": refund_data.get(
                "date_created", datetime.now().strftime("%Y-%m-%d")
            ),
            "journal_id": order.company_id.account_sale_journal_id.id,  # Adjust as needed
        }
        refund = request.env["account.move"].sudo().create(refund_vals)
        refund.action_post()
        _logger.info(
            "Created refund %s for BigCommerce order %s", refund.name, order_id
        )

        # Update order's refunded amount
        order.with_user(2).write(
            {
                "bigcommerce_refunded_amount": float(
                    order.bigcommerce_refunded_amount or 0.0
                )
                + refund_amount
            }
        )

    def _process_product_created(self, store, data):
        """Process store/product/created webhook: Create a new product in Odoo."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        product_id = data.get("id")
        if not product_id:
            error_msg = (
                f"Product ID missing in webhook data for store {store.store_hash}"
            )
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process product creation webhook: Product ID missing",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise ValidationError("Product ID missing in webhook data")

        try:
            # Check if product already exists
            existing_product = (
                store.env["product.template"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_store_id", "=", store.id),
                        ("bigcommerce_product_id", "=", str(product_id)),
                    ],
                    limit=1,
                )
            )
            if existing_product:
                _logger.info("Product %s already exists in Odoo", product_id)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product {product_id} already exists in Odoo (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                return

            # Fetch product details
            product_data = self._fetch_product_details(store, product_id)
            if not product_data:
                error_msg = f"Failed to fetch product details for product {product_id} from BigCommerce (store {store.store_hash})"
                _logger.error(error_msg)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Failed to fetch product details for product {product_id}",
                    status="failure",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid,
                )
                raise ValidationError(
                    "Failed to fetch product details from BigCommerce"
                )
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched product details for product {product_id} (store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )

            # Create product template
            product_vals = self._map_product_data(store, product_data)
            product = store.env["product.template"].sudo().create(product_vals)
            _logger.info(
                "Created product template %s for BigCommerce product %s",
                product.name,
                product_id,
            )
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Created product template {product.name} for BigCommerce product {product_id} (store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )

            # Import variants
            product.with_user(2).import_bigcommerce_variants()
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Triggered variant import for product {product.name} (BigCommerce product {product_id}, store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )

        except Exception as e:
            error_msg = f"Error processing product creation webhook for product {product_id} (store {store.store_hash}): {str(e)}"
            _logger.exception(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing product creation webhook for product {product_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise ValidationError(f"Error processing product: {str(e)}")

    def _process_product_updated(self, store, data):
        """Process store/product/updated webhook: Update existing product in Odoo."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        product_id = data.get("id")
        if not product_id:
            error_msg = (
                f"Product ID missing in webhook data for store {store.store_hash}"
            )
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process product update webhook: Product ID missing",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise ValidationError("Product ID missing in webhook data")

        try:
            # Find existing product
            product = (
                store.env["product.template"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_store_id", "=", store.id),
                        ("bigcommerce_product_id", "=", str(product_id)),
                    ],
                    limit=1,
                )
            )
            if not product:
                _logger.warning("Product %s not found in Odoo", product_id)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product {product_id} not found in Odoo for update (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                return

            # Fetch updated product details
            product_data = self._fetch_product_details(store, product_id)
            if not product_data:
                error_msg = f"Failed to fetch product details for product {product_id} from BigCommerce (store {store.store_hash})"
                _logger.error(error_msg)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Failed to fetch product details for product {product_id}",
                    status="failure",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid,
                )
                raise ValidationError("Failed to fetch updated product details")
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched product details for product {product_id} (store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )

            # Update product template
            product_vals = self._map_product_data(store, product_data)
            product.with_user(2).write(product_vals)
            _logger.info(
                "Updated product template %s for BigCommerce product %s",
                product.name,
                product_id,
            )
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Updated product template {product.name} for BigCommerce product {product_id} (store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )

            # Update or create product variants
            for variant in product_data.get("variants", []):
                variant_product = (
                    store.env["product.product"]
                    .sudo()
                    .search(
                        [
                            ("bigcommerce_sku_id", "=", variant.get("id")),
                            ("product_tmpl_id", "=", product.id),
                            ("bigcommerce_store_id", "=", store.id),
                        ],
                        limit=1,
                    )
                )
                variant_vals = {
                    "bigcommerce_store_id": store.id,
                    "bigcommerce_product_id": str(variant.get("product_id")),
                    "bigcommerce_sku": variant.get("sku", ""),
                    "bigcommerce_sku_id": variant.get("id"),
                    "list_price": float(variant.get("price", 0.0)),
                    "standard_price": float(variant.get("cost_price", 0.0)),
                }
                if variant_product:
                    variant_product.with_user(2).write(variant_vals)
                    _logger.info(
                        "Updated product variant for BigCommerce product %s, SKU %s",
                        product_id,
                        variant.get("sku"),
                    )
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Updated product variant for BigCommerce product {product_id}, SKU {variant.get('sku')} (store {store.store_hash})",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )
                else:
                    variant_vals["product_tmpl_id"] = product.id
                    store.env["product.product"].sudo().create(variant_vals)
                    _logger.info(
                        "Created product variant for BigCommerce product %s, SKU %s",
                        product_id,
                        variant.get("sku"),
                    )
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Created product variant for BigCommerce product {product_id}, SKU {variant.get('sku')} (store {store.store_hash})",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )

        except Exception as e:
            error_msg = f"Error processing product update webhook for product {product_id} (store {store.store_hash}): {str(e)}"
            _logger.exception(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing product update webhook for product {product_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise ValidationError(f"Error processing product: {str(e)}")

    def _fetch_product_details(self, store, product_id):
        """Fetch product details from BigCommerce API."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": store.access_token,
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            product_data = response.json().get("data", {})
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched product details for product {product_id} (store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )
            return product_data
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch product {product_id} for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Failed to fetch product details for product {product_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            return False

    def _map_product_data(self, store, product_data):
        """Map BigCommerce product data to Odoo product template fields."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product_id = product_data.get("id", "unknown")
        try:
            product_vals = {
                "name": product_data.get("name", "Unknown Product"),
                "bigcommerce_store_id": store.id,
                "bigcommerce_product_id": str(product_data.get("id")),
                "bigcommerce_type": product_data.get("type"),
                "bigcommerce_description": product_data.get("description"),
                "bigcommerce_weight": float(product_data.get("weight", 0.0)),
                "bigcommerce_width": float(product_data.get("width", 0.0)),
                "bigcommerce_depth": float(product_data.get("depth", 0.0)),
                "bigcommerce_height": float(product_data.get("height", 0.0)),
                "bigcommerce_cost_price": float(product_data.get("cost_price", 0.0)),
                "bigcommerce_sale_price": float(product_data.get("price", 0.0)),
                "bigcommerce_map_price": float(product_data.get("map_price", 0.0)),
                "bigcommerce_tax_class_id": product_data.get("tax_class_id", 0),
                "bigcommerce_product_tax_code": product_data.get("tax_code", ""),
                "bigcommerce_calculated_price": float(
                    product_data.get("calculated_price", 0.0)
                ),
                "bigcommerce_categories": ",".join(
                    map(str, product_data.get("categories", []))
                ),
                "bigcommerce_brand_id": self._get_or_create_brand(
                    store, product_data.get("brand_id")
                )
                if product_data.get("brand_id")
                else False,
                "bigcommerce_option_set_id": product_data.get("option_set_id", 0),
                "bigcommerce_inventory_level": product_data.get("inventory_level", 0),
                "bigcommerce_tracking": product_data.get("inventory_tracking", "none"),
                "bigcommerce_total_sold": product_data.get("total_sold", 0),
                "bigcommerce_layout_file": product_data.get("layout_file", ""),
                "bigcommerce_upc": product_data.get("upc", ""),
                "bigcommerce_mpn": product_data.get("mpn", ""),
                "bigcommerce_gtin": product_data.get("gtin", ""),
                "bigcommerce_url": product_data.get("custom_url", {}).get("url", ""),
                "bigcommerce_is_visible": product_data.get("is_visible", False),
                "bigcommerce_availability": product_data.get("availability", ""),
                "bigcommerce_condition": product_data.get("condition", ""),
                "bigcommerce_page_title": product_data.get("page_title", ""),
                "bigcommerce_meta_description": product_data.get(
                    "meta_description", ""
                ),
                "bigcommerce_view_count": product_data.get("view_count", 0),
                "list_price": float(product_data.get("price", 0.0)),
                "standard_price": float(product_data.get("cost_price", 0.0)),
                "type": "consu",
                "is_storable": True,
            }

            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Mapped product data for product {product_id} (store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )
            return product_vals
        except Exception as e:
            error_msg = f"Failed to map product data for product {product_id} for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Failed to map product data for product {product_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise

    def _get_or_create_brand(self, store, brand_id):
        """Get or create a BigCommerce brand."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        _logger.info(
            "Created store %s for BigCommerce brand ID %s", store, brand_id
        )  # Retained original log
        try:
            brand = (
                store.env["bigcommerce.brand"]
                .sudo()
                .search(
                    [("store_id", "=", store.id), ("brand_id", "=", brand_id)], limit=1
                )
            )
            if brand:
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Found brand {brand.name} for BigCommerce brand ID {brand_id} (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                _logger.info(
                    "Created store %s for BigCommerce brand ID %s", brand, brand.id
                )  # Retained original log
                return brand.id

            if brand_id:
                # Fetch brand details
                url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/brands/{brand_id}"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Auth-Token": store.access_token,
                }
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    brand_data = response.json().get("data", {})
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Fetched brand details for BigCommerce brand ID {brand_id} (store {store.store_hash})",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )
                    brand = (
                        store.env["bigcommerce.brand"]
                        .sudo()
                        .create(
                            {
                                "store_id": store.id,
                                "brand_id": brand_id,
                                "name": brand_data.get("name", f"Brand {brand_id}"),
                            }
                        )
                    )
                    _logger.info(
                        "Created brand %s for BigCommerce brand ID %s",
                        brand.name,
                        brand_id,
                    )
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Created brand {brand.name} for BigCommerce brand ID {brand_id} (store {store.store_hash})",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )
                except requests.exceptions.RequestException as e:
                    error_msg = f"Failed to fetch brand {brand_id} for store {store.store_hash}: {str(e)}"
                    _logger.error(error_msg)
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Failed to fetch brand details for BigCommerce brand ID {brand_id}",
                        status="failure",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message=error_msg,
                        cr_user_id=request.uid,
                    )
                    brand = (
                        store.env["bigcommerce.brand"]
                        .sudo()
                        .create(
                            {
                                "store_id": store.id,
                                "brand_id": brand_id,
                                "name": f"Brand {brand_id}",
                            }
                        )
                    )
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Created fallback brand Brand {brand_id} for BigCommerce brand ID {brand_id} (store {store.store_hash})",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )
            else:
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"No brand ID provided for store {store.store_hash}, returning False",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                return False

            _logger.info(
                "Created store %s for BigCommerce brand ID %s", brand, brand.id
            )  # Retained original log
            return brand.id

        except Exception as e:
            error_msg = f"Error processing brand for BigCommerce brand ID {brand_id} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing brand for BigCommerce brand ID {brand_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise

    def _process_product_inventory_updated(self, store, data):
        """Process store/product/inventory/updated webhook: Update product inventory in Odoo for non-variant products."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product_id = data.get("id")
        inventory_data = data.get("inventory", {})

        if not product_id or not inventory_data:
            error_msg = f"Product ID or inventory data missing in webhook data for store {store.store_hash}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process inventory update: Product ID or inventory data missing",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise ValidationError(
                "Product ID or inventory data missing in webhook data"
            )

        # Validate inventory data
        method = inventory_data.get("method")
        value = inventory_data.get("value")
        if not method or value is None:
            error_msg = f"Inventory method or value missing in webhook data for product {product_id} (store {store.store_hash})"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process inventory update: Inventory method or value missing",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise ValidationError("Inventory method or value missing in webhook data")

        try:
            # Find product template
            product_tmpl = (
                store.env["product.template"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_store_id", "=", store.id),
                        ("bigcommerce_product_id", "=", str(product_id)),
                    ],
                    limit=1,
                )
            )

            if not product_tmpl:
                _logger.warning("Product %s not found in Odoo", product_id)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product {product_id} not found in Odoo for inventory update (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                return {
                    "status": "success",
                    "message": f"Product {product_id} not found",
                }

            # Check if product has exactly one variant (non-variant product)
            if len(product_tmpl.product_variant_ids) != 1:
                _logger.warning(
                    "Product %s has multiple variants (%s) and is not managed by this webhook. Use variant-specific API.",
                    product_id,
                    len(product_tmpl.product_variant_ids),
                )
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product {product_id} has {len(product_tmpl.product_variant_ids)} variants and is not managed by this webhook (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                return {
                    "status": "success",
                    "message": f"Product {product_id} has multiple variants",
                }

            # Get the single product variant
            product = product_tmpl.product_variant_ids
            if not product:
                _logger.warning("No variant found for product %s", product_id)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"No variant found for product {product_id} (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                return {
                    "status": "success",
                    "message": f"No variant for product {product_id}",
                }

            # Get default warehouse and location
            warehouse = (
                store.env["stock.warehouse"]
                .sudo()
                .search(
                    [("company_id", "=", http.request.env.user.company_id.id)], limit=1
                )
            )
            if not warehouse:
                error_msg = (
                    f"No warehouse found for company in store {store.store_hash}"
                )
                _logger.error(error_msg)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message="Failed to process inventory update: No warehouse found",
                    status="failure",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid,
                )
                raise ValidationError("No warehouse found for the company")

            location = warehouse.lot_stock_id
            if not location:
                error_msg = (
                    f"No stock location found for warehouse in store {store.store_hash}"
                )
                _logger.error(error_msg)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message="Failed to process inventory update: No stock location found",
                    status="failure",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid,
                )
                raise ValidationError("No stock location found for the warehouse")

            # Search for existing stock.quant record
            quant = (
                store.env["stock.quant"]
                .sudo()
                .search(
                    [
                        ("product_id", "=", product.id),
                        ("location_id", "=", location.id),
                    ],
                    limit=1,
                )
            )

            # Use inventory_mode and system user (ID 2) for adjustments
            quant_env = (
                store.env["stock.quant"].with_context(inventory_mode=True).with_user(2)
            )

            if quant:
                # Update existing quant
                quant.with_user(2).write({"inventory_quantity": max(0, value)})
                quant.with_user(2)._apply_inventory()
                _logger.info(
                    "Updated stock.quant for product %s (ID %s) in location %s with quantity %s (method: %s)",
                    product_tmpl.name,
                    product_id,
                    location.name,
                    value,
                    method,
                )
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Updated stock for product {product_tmpl.name} (BigCommerce product ID {product_id}) with quantity {value} (method: {method}) in location {location.name} (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
            else:
                # Create new quant
                quant_env.with_user(2).create(
                    {
                        "product_id": product.id,
                        "location_id": location.id,
                        "inventory_quantity": max(0, value),
                    }
                )._apply_inventory()
                _logger.info(
                    "Created stock.quant for product %s (ID %s) in location %s with quantity %s (method: %s)",
                    product_tmpl.name,
                    product_id,
                    location.name,
                    value,
                    method,
                )
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Created stock for product {product_tmpl.name} (BigCommerce product ID {product_id}) with quantity {value} (method: {method}) in location {location.name} (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )

            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Inventory updated for BigCommerce product {product_id} (store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )
            return {
                "status": "success",
                "message": f"Inventory updated for product {product_id}",
            }

        except Exception as e:
            error_msg = f"Error processing inventory update for product {product_id} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing inventory update for product {product_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            raise ValidationError(f"Error processing inventory update: {str(e)}")

    def _process_sku_inventory_updated(self, store, data):
        """Process store/sku/inventory/updated webhook: Update variant inventory in Odoo."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sku_id = data.get("id")
        product_id = data.get("inventory", {}).get("product_id")
        variant_id = data.get("inventory", {}).get("variant_id")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": store.access_token,
        }

        if not (product_id and variant_id):
            error_msg = f"Missing product ID or variant ID in webhook data for store {store.store_hash}: {data}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process SKU inventory update: Missing product ID or variant ID",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            return {"status": "error", "message": "Missing product ID or variant ID"}

        try:
            # Fetch all inventory locations
            locations_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations"
            try:
                response = requests.get(locations_url, headers=headers)
                response.raise_for_status()
                locations = response.json()["data"]
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Fetched {len(locations)} inventory locations for store {store.store_hash}",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                if not locations:
                    _logger.warning("No locations found for store %s", store.store_hash)
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"No locations found for store {store.store_hash}",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )
                    return {"status": "success", "message": "No locations found"}
            except requests.exceptions.RequestException as e:
                error_msg = (
                    f"Failed to fetch locations for store {store.store_hash}: {str(e)}"
                )
                _logger.error(error_msg)
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message="Failed to fetch inventory locations",
                    status="failure",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid,
                )
                return {
                    "status": "error",
                    "message": f"Failed to fetch locations: {str(e)}",
                }

            # Find product variant
            product = (
                store.env["product.product"]
                .sudo()
                .search(
                    [
                        ("bigcommerce_store_id", "=", store.id),
                        ("bigcommerce_product_id", "=", str(product_id)),
                        ("bigcommerce_product_attribute_id", "=", str(variant_id)),
                    ],
                    limit=1,
                )
            )

            if not product:
                _logger.warning(
                    "Product not found for product ID %s, variant ID %s, store %s",
                    product_id,
                    variant_id,
                    store.store_hash,
                )
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product not found for product ID {product_id}, variant ID {variant_id} (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                return {
                    "status": "success",
                    "message": f"Product not found for product {product_id}, variant {variant_id}",
                }

            # Process inventory for each location
            found = False
            for location in locations:
                location_id = location["id"]
                if not location["enabled"]:
                    _logger.info(
                        "Skipping disabled location %s for store %s",
                        location_id,
                        store.store_hash,
                    )
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Skipped disabled location {location_id} for store {store.store_hash}",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )
                    continue

                # Fetch inventory items for the location
                url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations/{location_id}/items"
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    items = response.json()["data"]
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Fetched {len(items)} inventory items for location {location_id} (store {store.store_hash})",
                        status="success",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message="",
                        cr_user_id=request.uid,
                    )
                except requests.exceptions.RequestException as e:
                    _logger.warning(
                        "Failed to fetch inventory for location %s, store %s: %s",
                        location_id,
                        store.store_hash,
                        str(e),
                    )
                    store.env["cr.data.processing.log"]._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Failed to fetch inventory items for location {location_id} (store {store.store_hash})",
                        status="failure",
                        timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        initiated_at=initiated_at,
                        error_message=f"Failed to fetch inventory: {str(e)}",
                        cr_user_id=request.uid,
                    )
                    continue

                # Find the item matching product_id and variant_id
                for item in items:
                    identity = item["identity"]
                    if str(identity["product_id"]) != str(product_id) or str(
                        identity["variant_id"]
                    ) != str(variant_id):
                        continue

                    found = True
                    if not item["settings"]["is_in_stock"]:
                        _logger.info(
                            "Skipping out-of-stock item for SKU %s at location %s",
                            identity["sku"],
                            location_id,
                        )
                        store.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Skipped out-of-stock item for SKU {identity['sku']} at location {location_id} (store {store.store_hash})",
                            status="success",
                            timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            initiated_at=initiated_at,
                            error_message="",
                            cr_user_id=request.uid,
                        )
                        continue

                    # Find stock location
                    stock_location = (
                        store.env["stock.location"]
                        .sudo()
                        .search(
                            [
                                ("bc_location_id", "=", str(location_id)),
                                ("bigcommerce_store_id", "=", store.id),
                            ],
                            limit=1,
                        )
                    )

                    if not stock_location:
                        _logger.warning(
                            "Stock location not found for location ID %s, store %s, SKU %s",
                            location_id,
                            store.store_hash,
                            identity["sku"],
                        )
                        store.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Stock location not found for location ID {location_id}, SKU {identity['sku']} (store {store.store_hash})",
                            status="success",
                            timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            initiated_at=initiated_at,
                            error_message="",
                            cr_user_id=request.uid,
                        )
                        continue

                    # Update stock.quant
                    quant = (
                        store.env["stock.quant"]
                        .sudo()
                        .search(
                            [
                                ("product_id", "=", product.id),
                                ("location_id", "=", stock_location.id),
                            ],
                            limit=1,
                        )
                    )

                    # Calculate quantity (available_to_sell - safety_stock, minimum 0)
                    quantity = (
                        item["available_to_sell"] - item["settings"]["safety_stock"]
                    )
                    quantity = max(0, quantity)

                    quant_env = (
                        store.env["stock.quant"]
                        .with_context(inventory_mode=True)
                        .with_user(2)
                    )

                    if quant:
                        quant.with_user(2).write(
                            {
                                "inventory_quantity": quantity,
                                "inventory_date": fields.Datetime.now(),
                            }
                        )
                        quant.with_user(2)._apply_inventory()
                        _logger.info(
                            "Updated stock.quant for SKU %s (product ID %s, variant ID %s) at location %s with quantity %s",
                            identity["sku"],
                            product_id,
                            variant_id,
                            stock_location.name,
                            quantity,
                        )
                        store.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Updated stock for SKU {identity['sku']} (product ID {product_id}, variant ID {variant_id}) with quantity {quantity} at location {stock_location.name} (store {store.store_hash})",
                            status="success",
                            timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            initiated_at=initiated_at,
                            error_message="",
                            cr_user_id=request.uid,
                        )
                    else:
                        quant_env.with_user(2).create(
                            {
                                "product_id": product.id,
                                "location_id": stock_location.id,
                                "inventory_quantity": quantity,
                                "inventory_date": fields.Datetime.now(),
                            }
                        )._apply_inventory()
                        _logger.info(
                            "Created stock.quant for SKU %s (product ID %s, variant ID %s) at location %s with quantity %s",
                            identity["sku"],
                            product_id,
                            variant_id,
                            stock_location.name,
                            quantity,
                        )
                        store.env["cr.data.processing.log"]._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Created stock for SKU {identity['sku']} (product ID {product_id}, variant ID {variant_id}) with quantity {quantity} at location {stock_location.name} (store {store.store_hash})",
                            status="success",
                            timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            initiated_at=initiated_at,
                            error_message="",
                            cr_user_id=request.uid,
                        )

            if not found:
                _logger.warning(
                    "No inventory data found for product ID %s, variant ID %s, store %s",
                    product_id,
                    variant_id,
                    store.store_hash,
                )
                store.env["cr.data.processing.log"]._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"No inventory data found for product ID {product_id}, variant ID {variant_id} (store {store.store_hash})",
                    status="success",
                    timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    initiated_at=initiated_at,
                    error_message="",
                    cr_user_id=request.uid,
                )
                return {
                    "status": "success",
                    "message": f"No inventory data for product {product_id}, variant {variant_id}",
                }

            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Inventory updated for product ID {product_id}, variant ID {variant_id} (store {store.store_hash})",
                status="success",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message="",
                cr_user_id=request.uid,
            )
            return {
                "status": "success",
                "message": f"Inventory updated for product {product_id}, variant {variant_id}",
            }

        except Exception as e:
            error_msg = f"Error processing SKU inventory update for product {product_id}, variant {variant_id} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env["cr.data.processing.log"]._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing SKU inventory update for product ID {product_id}, variant ID {variant_id}",
                status="failure",
                timespan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid,
            )
            return {
                "status": "error",
                "message": f"Error processing SKU inventory update: {str(e)}",
            }
