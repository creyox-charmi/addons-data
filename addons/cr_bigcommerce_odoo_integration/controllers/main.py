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
import fnmatch
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
                _logger.info(f'store/order/created')
                return self._process_order_webhook(
                    store, webhook_data, headers, is_update=False
                )
            elif scope == "store/order/updated":
                _logger.info(f'store/order/updated')
                return self._process_order_webhook(
                    store, webhook_data, headers, is_update=True
                )
            elif scope == "store/order/refunded/created":
                return self._process_order_refunded(store, webhook_data)
            elif scope == "store/product/created":
                return self._process_product_created(store, webhook_data)
            elif scope == "store/product/updated":
                return self._process_product_updated(store, webhook_data)
            elif fnmatch.fnmatch(scope, "store/channel/*/inventory/product/stock_changed"):
                _logger.info("Matched wildcard scope: store/channel/*/inventory/product/stock_changed")
                variant_id = webhook_data.get("variant_id")
                _logger.info(f'variant_id {variant_id}')
                product_id = webhook_data.get("product_id")
                _logger.info(f'product_id {product_id}')
                location_id = webhook_data.get("location_id")
                _logger.info(f'location_id {location_id}')
                inventory = self.get_inventory_at_location(store, variant_id, product_id, location_id)
                _logger.info(f'inventory {inventory}')
                self._process_sku_inventory_updated(store, variant_id, product_id, location_id, inventory)
                _logger.info(
                    f"[BigCommerce] Inventory for variant_id={variant_id} at location_id={location_id}: {inventory}")

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
                    partner_id = user.partner_id
                    if group in user.group_ids:
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

    def get_inventory_at_location(self,store, variant_id, product_id, location_id):
        """
        Get total inventory on hand for a specific product variant at a specific location from BigCommerce.

        :param store: bigcommerce.store record
        :param variant_id: int
        :param product_id: int
        :param location_id: int
        :return: int (total_inventory_onhand) or None
        """
        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/items"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        params = {
            "variant_id:in": variant_id,  # filter by variant_id
            "limit": 1,
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            _logger.info(f"[BigCommerce] Inventory fetch response: {data}")

            items = data.get("data", [])
            if not items:
                _logger.warning(f"[BigCommerce] No inventory items found for variant_id {variant_id}")
                return None

            # Loop through locations to find the matching location_id
            for loc in items[0].get("locations", []):
                if loc.get("location_id") == location_id:
                    return loc.get("total_inventory_onhand")

            _logger.warning(f"[BigCommerce] No matching location {location_id} for variant_id {variant_id}")
            return None

        except requests.exceptions.RequestException as e:
            _logger.error(f"[BigCommerce] Inventory API request failed: {str(e)}")
            return None

    def _process_sku_inventory_updated(self, store, variant_id, product_id, location_id, quantity):
        """Process store/sku/inventory/updated webhook: Update variant inventory in Odoo."""
        _logger.info(
            f"Starting inventory update process: store={store.name}, product_id={product_id}, variant_id={variant_id}, location_id={location_id}, quantity={quantity}")

        if not (product_id and variant_id):
            _logger.warning("Missing product ID or variant ID in webhook payload")
            return {"status": "error", "message": "Missing product ID or variant ID"}

        try:
            _logger.info("Searching for matching product in Odoo...")
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
                    f"No matching product found in Odoo for product_id={product_id}, variant_id={variant_id}"
                )
                return {
                    "status": "success",
                    "message": "Product variant not found in Odoo",
                }

            _logger.info(f"Product found: {product.display_name} (ID: {product.id})")

            _logger.info("Searching for matching stock location...")
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
                _logger.warning(f"No matching stock location found for location_id={location_id}")
            else:
                _logger.info(f"Stock location found: {stock_location.complete_name} (ID: {stock_location.id})")

            if product and stock_location:
                _logger.info("Checking for existing quant...")
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

                quant_env = (
                    store.env["stock.quant"]
                    .with_context(inventory_mode=True)
                    .with_user(2)
                )

                if quant:
                    _logger.info(f"Existing quant found (ID: {quant.id}). Updating quantity...")
                    quant.with_user(2).write(
                        {
                            "inventory_quantity": quantity,
                            "inventory_date": fields.Datetime.now(),
                        }
                    )
                    quant.with_user(2)._apply_inventory()
                    _logger.info(
                        f"Updated existing quant for SKU {variant_id} at {stock_location.name} with quantity {quantity}"
                    )
                else:
                    _logger.info("No quant found. Creating new quant...")
                    quant_env.create(
                        {
                            "product_id": product.id,
                            "location_id": stock_location.id,
                            "inventory_quantity": quantity,
                            "inventory_date": fields.Datetime.now(),
                        }
                    )._apply_inventory()
                    _logger.info(
                        f"Created new quant for SKU {variant_id} at {stock_location.name} with quantity {quantity}"
                    )

            _logger.info(
                f"Inventory successfully updated for product ID {product_id}, variant ID {variant_id}"
            )
            return {
                "status": "success",
                "message": f"Inventory updated for product {product_id}, variant {variant_id}",
            }

        except Exception as e:
            error_msg = f"Exception while processing SKU inventory update for product_id={product_id}, variant_id={variant_id}, store={store.store_hash}: {str(e)}"
            _logger.exception(error_msg)
            return {
                "status": "error",
                "message": f"Error processing SKU inventory update: {str(e)}",
            }

