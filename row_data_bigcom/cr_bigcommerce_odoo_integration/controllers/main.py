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
    @http.route('/webhooks', type='json', auth='public', methods=['POST'], csrf=False)
    def handle_webhook(self):
        """Handle incoming webhooks from BigCommerce."""
        _logger.info("Received BigCommerce webhook request")
        try:
            # Parse JSON payload
            raw_data = request.httprequest.data.decode('UTF-8')
            payload = json.loads(raw_data)

            # Validate payload
            if not payload or 'scope' not in payload or 'data' not in payload:
                _logger.error("Invalid webhook payload: %s", raw_data)
                return {'status': 'error', 'message': 'Invalid payload'}

            scope = payload['scope']
            _logger.info(f"scope {scope}")
            producer = payload.get('producer', '')
            store_hash = producer.split('/')[-1] if producer and '/' in producer else None
            if not store_hash:
                _logger.error("No store_hash found in producer: %s", producer)
                return {'status': 'error', 'message': 'Store hash not found'}

            webhook_data = payload.get('data', {})

            # Find BigCommerce store
            store = request.env['bigcommerce.store'].sudo().search([('store_hash', '=', store_hash)], limit=1)
            if not store:
                _logger.error("No BigCommerce store found for store_hash: %s", store_hash)
                return {'status': 'error', 'message': 'Store not found'}


            # Prepare headers for API calls
            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            # Process webhook based on scope
            if scope == 'store/order/created':
                return self._process_order_webhook(store, webhook_data, headers, is_update=False)
            elif scope == 'store/order/updated':
                _logger.info('>>>>>>>>>>>>>>>>>update')
                return self._process_order_webhook(store, webhook_data, headers, is_update=True)
            elif scope == 'store/order/refunded/created':
                return self._process_order_refunded(store, webhook_data)
            elif scope == 'store/product/created':
                return self._process_product_created(store, webhook_data)
            elif scope == 'store/product/updated':
                return self._process_product_updated(store, webhook_data)
            elif scope == 'store/product/inventory/updated':
                return self._process_product_inventory_updated(store, webhook_data)
            elif scope == 'store/sku/inventory/updated':
                return self._process_sku_inventory_updated(store, webhook_data)
            else:
                _logger.warning("Unsupported webhook scope: %s", scope)
                return {'status': 'error', 'message': 'Unsupported scope'}

        except json.JSONDecodeError as e:
            _logger.error("Invalid JSON in webhook payload: %s", str(e))
            return {'status': 'error', 'message': 'Invalid JSON payload'}
        except Exception as e:
            _logger.exception("Error processing webhook: %s", str(e))
            return {'status': 'error', 'message': f'Error processing webhook: {str(e)}'}

    # before logger
    # def _process_order_webhook(self, store, webhook_data, headers, is_update=False):
    #     """Process order creation or update webhook by fetching full order data."""
    #     order_id = webhook_data.get('id')
    #     if not order_id:
    #         _logger.error("No order ID in webhook data: %s", webhook_data)
    #         return {'status': 'error', 'message': 'No order ID provided'}
    #
    #     # Fetch full order data from BigCommerce API
    #     order_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order_id}"
    #     try:
    #         response = requests.get(order_url, headers=headers)
    #         response.raise_for_status()
    #         order_data = response.json()
    #     except requests.exceptions.RequestException as e:
    #         _logger.error("Failed to fetch order %s: %s", order_id, str(e))
    #         return {'status': 'error', 'message': f'Failed to fetch order: {str(e)}'}
    #
    #     # Process order
    #     if is_update:
    #         sale_order = store.env['sale.order'].sudo().search([
    #             ('bigcommerce_order_id', '=', order_id)
    #         ], limit=1)
    #         if not sale_order:
    #             _logger.info("Order %s not found for update, treating as creation", order_id)
    #             # sale_order = store._process_bigcommerce_order(order_data, headers)
    #         else:
    #             sale_order = store._update_bigcommerce_order(order_data, headers, sale_order)
    #     else:
    #         sale_order = store._process_bigcommerce_order(order_data, headers)
    #
    #     if sale_order:
    #         return {
    #             'status': 'success',
    #             'message': f"Order {order_id} processed successfully",
    #             'odoo_order_id': sale_order.id,
    #             'odoo_order_name': sale_order.name
    #         }
    #     else:
    #         return {
    #             'status': 'error',
    #             'message': f"Failed to process order {order_id}"
    #         }


    # @http.route('/webhooks', type='json', auth='public', methods=['POST'], csrf=False)
    # def handle_webhook(self):
    #     """Handle incoming webhooks from BigCommerce."""
    #     _logger.info("Received BigCommerce webhook request")
    #     try:
    #         # Parse JSON payload
    #         raw_data = request.httprequest.data.decode('UTF-8')
    #         payload = json.loads(raw_data)

    #         # Validate payload
    #         if not payload or 'scope' not in payload or 'data' not in payload:
    #             _logger.error("Invalid webhook payload: %s", raw_data)
    #             return {'status': 'error', 'message': 'Invalid payload'}

    #         scope = payload['scope']
    #         producer = payload.get('producer', '')
    #         store_hash = producer.split('/')[-1] if producer and '/' in producer else None
    #         if not store_hash:
    #             _logger.error("No store_hash found in producer: %s", producer)
    #             return {'status': 'error', 'message': 'Store hash not found'}

    #         webhook_data = payload.get('data', {})

    #         # Find BigCommerce store
    #         store = request.env['bigcommerce.store'].sudo().search([('store_hash', '=', store_hash)], limit=1)
    #         if not store:
    #             _logger.error("No BigCommerce store found for store_hash: %s", store_hash)
    #             return {'status': 'error', 'message': 'Store not found'}

    #         # # Optional: Validate HMAC signature (if webhook secret is configured)
    #         # if store.webhook_secret:
    #         #     signature = request.httprequest.headers.get('X-Webhook-Signature')
    #         #     if not signature:
    #         #         _logger.error("Missing webhook signature for store %s", store_hash)
    #         #         return {'status': 'error', 'message': 'Missing webhook signature'}
    #         #     computed_signature = hmac.new(
    #         #         store.webhook_secret.encode('utf-8'),
    #         #         raw_data.encode('utf-8'),
    #         #         hashlib.sha256
    #         #     ).hexdigest()
    #         #     if not hmac.compare_digest(signature.encode('utf-8'), computed_signature.encode('utf-8')):
    #         #         _logger.error("Invalid webhook signature for store %s", store_hash)
    #         #         return {'status': 'error', 'message': 'Invalid webhook signature'}

    #         # Prepare headers for API calls
    #         headers = {
    #             "X-Auth-Token": store.access_token,
    #             "Accept": "application/json",
    #             "Content-Type": "application/json"
    #         }

    #         # Process webhook based on scope
    #         if scope in ['store/order/created', 'store/order/updated']:
    #             return self._process_order_webhook(store, webhook_data, headers)
    #         elif scope == 'store/order/refunded/created':
    #             return self._process_order_refunded(store, webhook_data)
    #         elif scope == 'store/product/created':
    #             return self._process_product_created(store, webhook_data)
    #         elif scope == 'store/product/updated':
    #             return self._process_product_updated(store, webhook_data)
    #         elif scope == 'store/product/inventory/updated':
    #             return self._process_product_inventory_updated(store, webhook_data)
    #         elif scope == 'store/sku/inventory/updated':
    #             return self._process_sku_inventory_updated(store, webhook_data)
    #         else:
    #             _logger.warning("Unsupported webhook scope: %s", scope)
    #             return {'status': 'error', 'message': 'Unsupported scope'}

    #     except json.JSONDecodeError as e:
    #         _logger.error("Invalid JSON in webhook payload: %s", str(e))
    #         return {'status': 'error', 'message': 'Invalid JSON payload'}
    #     except Exception as e:
    #         _logger.exception("Error processing webhook: %s", str(e))
    #         return {'status': 'error', 'message': f'Error processing webhook: {str(e)}'}

    def _process_order_webhook(self, store, webhook_data, headers, is_update=False):
        """Process order creation or update webhook by fetching full order data."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        order_id = webhook_data.get('id')
        if not order_id:
            error_msg = f"No order ID in webhook data for store {store.store_hash}: {webhook_data}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process order webhook: No order ID provided",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            return {'status': 'error', 'message': 'No order ID provided'}

        # Fetch full order data from BigCommerce API
        order_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order_id}"
        try:
            response = requests.get(order_url, headers=headers)
            response.raise_for_status()
            order_data = response.json()
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched order {order_id} data for store {store.store_hash}",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch order {order_id} for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Failed to fetch order {order_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            return {'status': 'error', 'message': f'Failed to fetch order: {str(e)}'}

        # Process order
        try:
            if is_update:
                sale_order = store.env['sale.order'].sudo().search([
                    ('bigcommerce_order_id', '=', order_id)
                ], limit=1)
                _logger.info(f' sale_order : {sale_order}')
                if not sale_order:
                    _logger.info("Order %s not found for update, treating as creation", order_id)
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Order {order_id} not found for update, treating as creation (store {store.store_hash})",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
                    # sale_order = store._process_bigcommerce_order(order_data, headers)
                else:
                    _logger.info('YES...........UPDATE')
                    sale_order = store._update_bigcommerce_order(order_data, headers, sale_order)
            else:
                sale_order = store._process_bigcommerce_order(order_data, headers)

            if sale_order:
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Successfully processed order {order_id} as {'update' if is_update else 'creation'} (Odoo order {sale_order.name}, store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return {
                    'status': 'success',
                    'message': f"Order {order_id} processed successfully",
                    'odoo_order_id': sale_order.id,
                    'odoo_order_name': sale_order.name
                }
            else:
                error_msg = f"Failed to process order {order_id} for store {store.store_hash}"
                _logger.error(error_msg)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Failed to process order {order_id} as {'update' if is_update else 'creation'}",
                    status='failure',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid
                )
                return {
                    'status': 'error',
                    'message': f"Failed to process order {order_id}"
                }

        except Exception as e:
            error_msg = f"Error processing order webhook {order_id} for store {store.store_hash}: {str(e)}"
            _logger.exception(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing order webhook {order_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            return {'status': 'error', 'message': f'Error processing order: {str(e)}'}

    # def _process_order_webhook(self, store, webhook_data, headers):
    #     """Process order creation or update webhook by fetching full order data."""
    #     order_id = webhook_data.get('id')
    #     if not order_id:
    #         _logger.error("No order ID in webhook data: %s", webhook_data)
    #         return {'status': 'error', 'message': 'No order ID provided'}

    #     # Fetch full order data from BigCommerce API
    #     order_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order_id}"
    #     try:
    #         response = requests.get(order_url, headers=headers)
    #         response.raise_for_status()
    #         order_data = response.json()
    #     except requests.exceptions.RequestException as e:
    #         _logger.error("Failed to fetch order %s: %s", order_id, str(e))
    #         return {'status': 'error', 'message': f'Failed to fetch order: {str(e)}'}

    #     # Process order using unified method
    #     sale_order = store._process_bigcommerce_order(order_data, headers)
    #     if sale_order:
    #         return {
    #             'status': 'success',
    #             'message': f"Order {order_id} processed successfully",
    #             'odoo_order_id': sale_order.id,
    #             'odoo_order_name': sale_order.name
    #         }
    #     else:
    #         return {
    #             'status': 'error',
    #             'message': f"Failed to process order {order_id}"
    #         }

    def _process_order_created(self, store, data):
        """Process store/order/created webhook: Create a new sales order in Odoo."""
        order_id = data.get('id')
        if not order_id:
            raise ValidationError("Order ID missing in webhook data")

        # Check if order already exists
        existing_order = request.env['sale.order'].sudo().search([
            ('bigcommerce_store_id', '=', store.id),
            ('bigcommerce_order_id', '=', str(order_id))
        ], limit=1)
        if existing_order:
            _logger.info("Order %s already exists in Odoo", order_id)
            return

        # Fetch order details from BigCommerce API
        order_data = self._fetch_order_details(store, order_id)
        if not order_data:
            raise ValidationError("Failed to fetch order details from BigCommerce")

        # Fetch order products
        products_data = self._fetch_order_products(store, order_id)

        # Map customer
        partner = self._get_or_create_partner(store, order_data.get('billing_address', {}))

        # Map order status
        status = self._get_or_create_order_status(store, order_data.get('status_id'), order_data.get('status'), order_data.get('custom_status'))

        # Create sales order
        order_vals = {
            'bigcommerce_store_id': store.id,
            'bigcommerce_order_id': str(order_id),
            'bigcommerce_order_status_id': status.id,
            'partner_id': partner.id,
            'date_order': datetime.strptime(order_data.get('date_created'), '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d %H:%M:%S'),
            'state': 'draft',
            'bigcommerce_subtotal_ex_tax': float(order_data.get('subtotal_ex_tax', 0.0)),
            'bigcommerce_subtotal_inc_tax': float(order_data.get('subtotal_inc_tax', 0.0)),
            'bigcommerce_subtotal_tax': float(order_data.get('subtotal_tax', 0.0)),
            'bigcommerce_base_shipping_cost': float(order_data.get('base_shipping_cost', 0.0)),
            'bigcommerce_shipping_cost_ex_tax': float(order_data.get('shipping_cost_ex_tax', 0.0)),
            'bigcommerce_shipping_cost_inc_tax': float(order_data.get('shipping_cost_inc_tax', 0.0)),
            'bigcommerce_total_ex_tax': float(order_data.get('total_ex_tax', 0.0)),
            'bigcommerce_total_inc_tax': float(order_data.get('total_inc_tax', 0.0)),
            'bigcommerce_total_tax': float(order_data.get('total_tax', 0.0)),
            'bigcommerce_payment_method': order_data.get('payment_method'),
            'bigcommerce_payment_status': order_data.get('payment_status'),
            'bigcommerce_refunded_amount': float(order_data.get('refunded_amount', 0.0)),
            'bigcommerce_discount_amount': float(order_data.get('discount_amount', 0.0)),
            'bigcommerce_customer_message': order_data.get('customer_message'),
            'bigcommerce_staff_notes': order_data.get('staff_notes'),
            'order_line': self._prepare_order_lines(store, products_data),
        }

        order = request.env['sale.order'].sudo().create(order_vals)
        _logger.info("Created sales order %s for BigCommerce order %s", order.name, order_id)

        # Confirm order based on BigCommerce status
        if order_data.get('status') in ['Awaiting Payment', 'Awaiting Fulfillment', 'Awaiting Shipment']:
            order.action_confirm()

    def _process_order_updated(self, store, data):
        """Process store/order/updated webhook: Update existing sales order in Odoo."""
        order_id = data.get('id')
        if not order_id:
            raise ValidationError("Order ID missing in webhook data")

        # Find existing order
        order = request.env['sale.order'].sudo().search([
            ('bigcommerce_store_id', '=', store.id),
            ('bigcommerce_order_id', '=', str(order_id))
        ], limit=1)
        if not order:
            _logger.warning("Order %s not found in Odoo", order_id)
            return

        # Fetch updated order details
        order_data = self._fetch_order_details(store, order_id)
        if not order_data:
            raise ValidationError("Failed to fetch updated order details")

        # Fetch order products
        products_data = self._fetch_order_products(store, order_id)

        # Update order status
        status = self._get_or_create_order_status(store, order_data.get('status_id'), order_data.get('status'), order_data.get('custom_status'))

        # Update order fields
        order_vals = {
            'bigcommerce_order_status_id': status.id,
            'bigcommerce_subtotal_ex_tax': float(order_data.get('subtotal_ex_tax', 0.0)),
            'bigcommerce_subtotal_inc_tax': float(order_data.get('subtotal_inc_tax', 0.0)),
            'bigcommerce_subtotal_tax': float(order_data.get('subtotal_tax', 0.0)),
            'bigcommerce_base_shipping_cost': float(order_data.get('base_shipping_cost', 0.0)),
            'bigcommerce_shipping_cost_ex_tax': float(order_data.get('shipping_cost_ex_tax', 0.0)),
            'bigcommerce_shipping_cost_inc_tax': float(order_data.get('shipping_cost_inc_tax', 0.0)),
            'bigcommerce_total_ex_tax': float(order_data.get('total_ex_tax', 0.0)),
            'bigcommerce_total_inc_tax': float(order_data.get('total_inc_tax', 0.0)),
            'bigcommerce_total_tax': float(order_data.get('total_tax', 0.0)),
            'bigcommerce_payment_method': order_data.get('payment_method'),
            'bigcommerce_payment_status': order_data.get('payment_status'),
            'bigcommerce_refunded_amount': float(order_data.get('refunded_amount', 0.0)),
            'bigcommerce_discount_amount': float(order_data.get('discount_amount', 0.0)),
            'bigcommerce_customer_message': order_data.get('customer_message'),
            'bigcommerce_staff_notes': order_data.get('staff_notes'),
            'order_line': [(5, 0, 0)] + self._prepare_order_lines(store, products_data),  # Replace existing lines
        }
        order.with_user(2).write(order_vals)

        # Update status based on BigCommerce status
        bc_status = order_data.get('status')
        if bc_status == 'Cancelled' and order.state != 'cancel':
            order.action_cancel()
        elif bc_status in ['Awaiting Fulfillment', 'Awaiting Shipment'] and order.state == 'draft':
            order.action_confirm()

        _logger.info("Updated sales order %s for BigCommerce order %s", order.name, order_id)

    def _process_order_refunded(self, store, data):
        """Process store/order/refunded/created webhook: Create a refund in Odoo."""
        order_id = data.get('order_id')
        refund_data = data.get('refund', {})
        if not order_id or not refund_data:
            raise ValidationError("Order ID or refund data missing in webhook data")

        # Find existing order
        order = request.env['sale.order'].sudo().search([
            ('bigcommerce_store_id', '=', store.id),
            ('bigcommerce_order_id', '=', str(order_id))
        ], limit=1)
        if not order:
            _logger.warning("Order %s not found in Odoo for refund", order_id)
            return

        # Check if refund already processed
        refund_amount = float(refund_data.get('amount', 0.0))
        existing_refunded = request.env['account.move'].sudo().search([
            ('sale_order_id', '=', order.id),
            ('move_type', '=', 'out_refunded'),
            ('amount_total', '=', refund_amount)
        ], limit=1)
        if existing_refunded:
            _logger.info("Refund already processed for order %s", order_id)
            return

        # Create credit note (refund)
        refund_vals = {
            'move_type': 'out_refunded',
            'partner_id': order.partner_id.id,
            'sale_order_id': order.id,
            'amount_total': refund_amount,
            'invoice_date': refund_data.get('date_created', datetime.now().strftime('%Y-%m-%d')),
            'journal_id': order.company_id.account_sale_journal_id.id,  # Adjust as needed
        }
        refund = request.env['account.move'].sudo().create(refund_vals)
        refund.action_post()
        _logger.info("Created refund %s for BigCommerce order %s", refund.name, order_id)

        # Update order's refunded amount
        order.with_user(2).write({'bigcommerce_refunded_amount': float(order.bigcommerce_refunded_amount or 0.0) + refund_amount})

    # before logs
    # def _process_product_created(self, store, data):
    #     """Process store/product/created webhook: Create a new product in Odoo."""
    #     product_id = data.get('id')
    #     if not product_id:
    #         raise ValidationError("Product ID missing in webhook data")
    #
    #     # Check if product already exists
    #     existing_product = request.env['product.template'].sudo().search([
    #         ('bigcommerce_store_id', '=', store.id),
    #         ('bigcommerce_product_id', '=', str(product_id))
    #     ], limit=1)
    #     if existing_product:
    #         _logger.info("Product %s already exists in Odoo", product_id)
    #         return
    #
    #     # Fetch product details
    #     product_data = self._fetch_product_details(store, product_id)
    #     if not product_data:
    #         raise ValidationError("Failed to fetch product details from BigCommerce")
    #
    #     # Create product template
    #     product_vals = self._map_product_data(store, product_data)
    #     product = request.env['product.template'].sudo().create(product_vals)
    #     _logger.info("Created product template %s for BigCommerce product %s", product.name, product_id)
    #     product.with_user(2).import_bigcommerce_variants()
    #     # # Create product variant (product.product)
    #     # if product_data.get('variants'):
    #     #     for variant in product_data.get('variants', []):
    #     #         variant_vals = {
    #     #             'product_tmpl_id': product.id,
    #     #             'bigcommerce_product_id': str(variant.get('product_id')),
    #     #             'bigcommerce_sku': variant.get('sku', ''),
    #     #             'bigcommerce_sku_id': variant.get('id'),
    #     #             'list_price': float(variant.get('price', 0.0)),
    #     #             'standard_price': float(variant.get('cost_price', 0.0)),
    #     #         }
    #     #         request.env['product.product'].sudo().create(variant_vals)
    #     #         _logger.info("Created product variant for BigCommerce product %s, SKU %s", product_id, variant.get('sku'))

    def _process_product_created(self, store, data):
        """Process store/product/created webhook: Create a new product in Odoo."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        product_id = data.get('id')
        if not product_id:
            error_msg = f"Product ID missing in webhook data for store {store.store_hash}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process product creation webhook: Product ID missing",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise ValidationError("Product ID missing in webhook data")

        try:
            # Check if product already exists
            existing_product = store.env['product.template'].sudo().search([
                ('bigcommerce_store_id', '=', store.id),
                ('bigcommerce_product_id', '=', str(product_id))
            ], limit=1)
            if existing_product:
                _logger.info("Product %s already exists in Odoo", product_id)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product {product_id} already exists in Odoo (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return

            # Fetch product details
            product_data = self._fetch_product_details(store, product_id)
            if not product_data:
                error_msg = f"Failed to fetch product details for product {product_id} from BigCommerce (store {store.store_hash})"
                _logger.error(error_msg)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Failed to fetch product details for product {product_id}",
                    status='failure',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid
                )
                raise ValidationError("Failed to fetch product details from BigCommerce")
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched product details for product {product_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )

            # Create product template
            product_vals = self._map_product_data(store, product_data)
            product = store.env['product.template'].sudo().create(product_vals)
            _logger.info("Created product template %s for BigCommerce product %s", product.name, product_id)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Created product template {product.name} for BigCommerce product {product_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )

            # Import variants
            product.with_user(2).import_bigcommerce_variants()
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Triggered variant import for product {product.name} (BigCommerce product {product_id}, store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )

        except Exception as e:
            error_msg = f"Error processing product creation webhook for product {product_id} (store {store.store_hash}): {str(e)}"
            _logger.exception(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing product creation webhook for product {product_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise ValidationError(f"Error processing product: {str(e)}")

    # before logs
    # def _process_product_updated(self, store, data):
    #     """Process store/product/updated webhook: Update existing product in Odoo."""
    #     product_id = data.get('id')
    #     if not product_id:
    #         raise ValidationError("Product ID missing in webhook data")
    #
    #     # Find existing product
    #     product = request.env['product.template'].sudo().search([
    #         ('bigcommerce_store_id', '=', store.id),
    #         ('bigcommerce_product_id', '=', str(product_id))
    #     ], limit=1)
    #     if not product:
    #         _logger.warning("Product %s not found in Odoo", product_id)
    #         return
    #
    #     # Fetch updated product details
    #     product_data = self._fetch_product_details(store, product_id)
    #     if not product_data:
    #         raise ValidationError("Failed to fetch updated product details")
    #     _logger.info(f'>>>product_data : {product_data} ')
    #     # Update product template
    #     product_vals = self._map_product_data(store, product_data)
    #     product.with_user(2).write(product_vals)
    #     _logger.info("Updated product template %s for BigCommerce product %s", product.name, product_id)
    #
    #     # Update or create product variants
    #     for variant in product_data.get('variants', []):
    #         variant_product = request.env['product.product'].sudo().search([
    #             ('bigcommerce_sku_id', '=', variant.get('id')),
    #             ('product_tmpl_id', '=', product.id)
    #         ], limit=1)
    #         variant_vals = {
    #             'bigcommerce_product_id': str(variant.get('product_id')),
    #             'bigcommerce_sku': variant.get('sku', ''),
    #             'bigcommerce_sku_id': variant.get('id'),
    #             'list_price': float(variant.get('price', 0.0)),
    #             'standard_price': float(variant.get('cost_price', 0.0)),
    #         }
    #         if variant_product:
    #             variant_product.with_user(2).write(variant_vals)
    #             _logger.info("Updated product variant for BigCommerce product %s, SKU %s", product_id, variant.get('sku'))
    #         else:
    #             variant_vals['product_tmpl_id'] = product.id
    #             request.env['product.product'].sudo().create(variant_vals)
    #             _logger.info("Created product variant for BigCommerce product %s, SKU %s", product_id, variant.get('sku'))

    def _process_product_updated(self, store, data):
        """Process store/product/updated webhook: Update existing product in Odoo."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        product_id = data.get('id')
        if not product_id:
            error_msg = f"Product ID missing in webhook data for store {store.store_hash}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process product update webhook: Product ID missing",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise ValidationError("Product ID missing in webhook data")

        try:
            # Find existing product
            product = store.env['product.template'].sudo().search([
                ('bigcommerce_store_id', '=', store.id),
                ('bigcommerce_product_id', '=', str(product_id))
            ], limit=1)
            if not product:
                _logger.warning("Product %s not found in Odoo", product_id)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product {product_id} not found in Odoo for update (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return

            # Fetch updated product details
            product_data = self._fetch_product_details(store, product_id)
            if not product_data:
                error_msg = f"Failed to fetch product details for product {product_id} from BigCommerce (store {store.store_hash})"
                _logger.error(error_msg)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Failed to fetch product details for product {product_id}",
                    status='failure',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid
                )
                raise ValidationError("Failed to fetch updated product details")
            _logger.info(f'>>>product_data : {product_data} ')
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched product details for product {product_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )

            # Update product template
            product_vals = self._map_product_data(store, product_data)
            product.with_user(2).write(product_vals)
            _logger.info("Updated product template %s for BigCommerce product %s", product.name, product_id)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Updated product template {product.name} for BigCommerce product {product_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )

            # Update or create product variants
            for variant in product_data.get('variants', []):
                variant_product = store.env['product.product'].sudo().search([
                    ('bigcommerce_sku_id', '=', variant.get('id')),
                    ('product_tmpl_id', '=', product.id)
                ], limit=1)
                variant_vals = {
                    'bigcommerce_product_id': str(variant.get('product_id')),
                    'bigcommerce_sku': variant.get('sku', ''),
                    'bigcommerce_sku_id': variant.get('id'),
                    'list_price': float(variant.get('price', 0.0)),
                    'standard_price': float(variant.get('cost_price', 0.0)),
                }
                if variant_product:
                    variant_product.with_user(2).write(variant_vals)
                    _logger.info("Updated product variant for BigCommerce product %s, SKU %s", product_id,
                                 variant.get('sku'))
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Updated product variant for BigCommerce product {product_id}, SKU {variant.get('sku')} (store {store.store_hash})",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
                else:
                    variant_vals['product_tmpl_id'] = product.id
                    store.env['product.product'].sudo().create(variant_vals)
                    _logger.info("Created product variant for BigCommerce product %s, SKU %s", product_id,
                                 variant.get('sku'))
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Created product variant for BigCommerce product {product_id}, SKU {variant.get('sku')} (store {store.store_hash})",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )

        except Exception as e:
            error_msg = f"Error processing product update webhook for product {product_id} (store {store.store_hash}): {str(e)}"
            _logger.exception(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing product update webhook for product {product_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise ValidationError(f"Error processing product: {str(e)}")

    # before logs
    # def _fetch_order_details(self, store, order_id):
    #     """Fetch order details from BigCommerce API."""
    #     url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order_id}"
    #     headers = {
    #         'Accept': 'application/json',
    #         'Content-Type': 'application/json',
    #         'X-Auth-Token': store.access_token
    #     }
    #     try:
    #         response = requests.get(url, headers=headers)
    #         response.raise_for_status()
    #         return response.json()
    #     except requests.exceptions.RequestException as e:
    #         _logger.error("Failed to fetch order %s: %s", order_id, str(e))
    #         return False

    def _fetch_order_details(self, store, order_id):
        """Fetch order details from BigCommerce API."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order_id}"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Auth-Token': store.access_token
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            order_data = response.json()
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched order details for order {order_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return order_data
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch order {order_id} for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Failed to fetch order details for order {order_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            return False

    # before logs
    # def _fetch_order_products(self, store, order_id):
    #     """Fetch order products from BigCommerce API."""
    #     url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order_id}/products"
    #     headers = {
    #         'Accept': 'application/json',
    #         'Content-Type': 'application/json',
    #         'X-Auth-Token': store.access_token
    #     }
    #     try:
    #         response = requests.get(url, headers=headers)
    #         response.raise_for_status()
    #         return response.json()
    #     except requests.exceptions.RequestException as e:
    #         _logger.error("Failed to fetch products for order %s: %s", order_id, str(e))
    #         return []

    def _fetch_order_products(self, store, order_id):
        """Fetch order products from BigCommerce API."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order_id}/products"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Auth-Token': store.access_token
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            products_data = response.json()
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched {len(products_data)} products for order {order_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return products_data
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch products for order {order_id} for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Failed to fetch products for order {order_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            return []

    # before logs
    # def _fetch_product_details(self, store, product_id):
    #     """Fetch product details from BigCommerce API."""
    #     url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id}"
    #     headers = {
    #         'Accept': 'application/json',
    #         'Content-Type': 'application/json',
    #         'X-Auth-Token': store.access_token
    #     }
    #     try:
    #         response = requests.get(url, headers=headers)
    #         response.raise_for_status()
    #         return response.json().get('data', {})
    #     except requests.exceptions.RequestException as e:
    #         _logger.error("Failed to fetch product %s: %s", product_id, str(e))
    #         return False

    def _fetch_product_details(self, store, product_id):
        """Fetch product details from BigCommerce API."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/products/{product_id}"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Auth-Token': store.access_token
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            product_data = response.json().get('data', {})
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Fetched product details for product {product_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return product_data
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch product {product_id} for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Failed to fetch product details for product {product_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            return False

    #before logs
    # def _map_product_data(self, store, product_data):
    #     """Map BigCommerce product data to Odoo product template fields."""
    #     return {
    #         'name': product_data.get('name', 'Unknown Product'),
    #         'bigcommerce_store_id': store.id,
    #         'bigcommerce_product_id': str(product_data.get('id')),
    #         'bigcommerce_type': product_data.get('type'),
    #         'bigcommerce_description': product_data.get('description'),
    #         'bigcommerce_weight': float(product_data.get('weight', 0.0)),
    #         'bigcommerce_width': float(product_data.get('width', 0.0)),
    #         'bigcommerce_depth': float(product_data.get('depth', 0.0)),
    #         'bigcommerce_height': float(product_data.get('height', 0.0)),
    #         'bigcommerce_cost_price': float(product_data.get('cost_price', 0.0)),
    #         'bigcommerce_sale_price': float(product_data.get('price', 0.0)),
    #         'bigcommerce_map_price': float(product_data.get('map_price', 0.0)),
    #         'bigcommerce_tax_class_id': product_data.get('tax_class_id', 0),
    #         'bigcommerce_product_tax_code': product_data.get('tax_code', ''),
    #         'bigcommerce_calculated_price': float(product_data.get('calculated_price', 0.0)),
    #         'bigcommerce_categories': ','.join(map(str, product_data.get('categories', []))),
    #         'bigcommerce_brand_id': self._get_or_create_brand(store, product_data.get('brand_id')) if product_data.get('brand_id') else False,
    #         'bigcommerce_option_set_id': product_data.get('option_set_id', 0),
    #         'bigcommerce_inventory_level': product_data.get('inventory_level', 0),
    #         'bigcommerce_tracking': product_data.get('inventory_tracking', 'none'),
    #         'bigcommerce_total_sold': product_data.get('total_sold', 0),
    #         'bigcommerce_layout_file': product_data.get('layout_file', ''),
    #         'bigcommerce_upc': product_data.get('upc', ''),
    #         'bigcommerce_mpn': product_data.get('mpn', ''),
    #         'bigcommerce_gtin': product_data.get('gtin', ''),
    #         'bigcommerce_url': product_data.get('custom_url', {}).get('url', ''),
    #         'bigcommerce_is_visible': product_data.get('is_visible', False),
    #         'bigcommerce_availability': product_data.get('availability', ''),
    #         'bigcommerce_condition': product_data.get('condition', ''),
    #         'bigcommerce_page_title': product_data.get('page_title', ''),
    #         'bigcommerce_meta_description': product_data.get('meta_description', ''),
    #         'bigcommerce_view_count': product_data.get('view_count', 0),
    #         'list_price': float(product_data.get('price', 0.0)),
    #         'standard_price': float(product_data.get('cost_price', 0.0)),
    #         'detailed_type': 'product',
    #     }

    def _map_product_data(self, store, product_data):
        """Map BigCommerce product data to Odoo product template fields."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        product_id = product_data.get('id', 'unknown')

        try:
            product_vals = {
                'name': product_data.get('name', 'Unknown Product'),
                'bigcommerce_store_id': store.id,
                'bigcommerce_product_id': str(product_data.get('id')),
                'bigcommerce_type': product_data.get('type'),
                'bigcommerce_description': product_data.get('description'),
                'bigcommerce_weight': float(product_data.get('weight', 0.0)),
                'bigcommerce_width': float(product_data.get('width', 0.0)),
                'bigcommerce_depth': float(product_data.get('depth', 0.0)),
                'bigcommerce_height': float(product_data.get('height', 0.0)),
                'bigcommerce_cost_price': float(product_data.get('cost_price', 0.0)),
                'bigcommerce_sale_price': float(product_data.get('price', 0.0)),
                'bigcommerce_map_price': float(product_data.get('map_price', 0.0)),
                'bigcommerce_tax_class_id': product_data.get('tax_class_id', 0),
                'bigcommerce_product_tax_code': product_data.get('tax_code', ''),
                'bigcommerce_calculated_price': float(product_data.get('calculated_price', 0.0)),
                'bigcommerce_categories': ','.join(map(str, product_data.get('categories', []))),
                'bigcommerce_brand_id': self._get_or_create_brand(store, product_data.get('brand_id')) if product_data.get('brand_id') else False,
                'bigcommerce_option_set_id': product_data.get('option_set_id', 0),
                'bigcommerce_inventory_level': product_data.get('inventory_level', 0),
                'bigcommerce_tracking': product_data.get('inventory_tracking', 'none'),
                'bigcommerce_total_sold': product_data.get('total_sold', 0),
                'bigcommerce_layout_file': product_data.get('layout_file', ''),
                'bigcommerce_upc': product_data.get('upc', ''),
                'bigcommerce_mpn': product_data.get('mpn', ''),
                'bigcommerce_gtin': product_data.get('gtin', ''),
                'bigcommerce_url': product_data.get('custom_url', {}).get('url', ''),
                'bigcommerce_is_visible': product_data.get('is_visible', False),
                'bigcommerce_availability': product_data.get('availability', ''),
                'bigcommerce_condition': product_data.get('condition', ''),
                'bigcommerce_page_title': product_data.get('page_title', ''),
                'bigcommerce_meta_description': product_data.get('meta_description', ''),
                'bigcommerce_view_count': product_data.get('view_count', 0),
                'list_price': float(product_data.get('price', 0.0)),
                'standard_price': float(product_data.get('cost_price', 0.0)),
                'detailed_type': 'product',
            }
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Mapped product data for product {product_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return product_vals
        except Exception as e:
            error_msg = f"Failed to map product data for product {product_id} for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Failed to map product data for product {product_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise

    # before
    # def _get_or_create_brand(self, store, brand_id):
    #     """Get or create a BigCommerce brand."""
    #     _logger.info("Created store %s for BigCommerce brand ID %s", store, brand_id)
    #     brand = request.env['bigcommerce.brand'].sudo().search([
    #         ('store_id', '=', store.id),
    #         ('brand_id', '=', brand_id)
    #     ], limit=1)
    #     if not brand and brand_id:
    #         # Fetch brand details (simplified)
    #         url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/brands/{brand_id}"
    #         headers = {
    #             'Accept': 'application/json',
    #             'Content-Type': 'application/json',
    #             'X-Auth-Token': store.access_token
    #         }
    #         try:
    #             response = requests.get(url, headers=headers)
    #             response.raise_for_status()
    #             brand_data = response.json().get('data', {})
    #             brand = request.env['bigcommerce.brand'].sudo().create({
    #                 'store_id': store.id,
    #                 'brand_id': brand_id,
    #                 'name': brand_data.get('name', f"Brand {brand_id}"),
    #             })
    #             _logger.info("Created brand %s for BigCommerce brand ID %s", brand.name, brand_id)
    #         except requests.exceptions.RequestException as e:
    #             _logger.error("Failed to fetch brand %s: %s", brand_id, str(e))
    #             brand = request.env['bigcommerce.brand'].sudo().create({
    #                 'store_id': store.id,
    #                 'brand_id': brand_id,
    #                 'name': f"Brand {brand_id}",
    #             })
    #     _logger.info("Created store %s for BigCommerce brand ID %s", brand, brand.id)
    #     return brand.id

    def _get_or_create_brand(self, store, brand_id):
        """Get or create a BigCommerce brand."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        _logger.info("Created store %s for BigCommerce brand ID %s", store, brand_id)  # Retained original log
        try:
            brand = store.env['bigcommerce.brand'].sudo().search([
                ('store_id', '=', store.id),
                ('brand_id', '=', brand_id)
            ], limit=1)
            if brand:
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Found brand {brand.name} for BigCommerce brand ID {brand_id} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                _logger.info("Created store %s for BigCommerce brand ID %s", brand, brand.id)  # Retained original log
                return brand.id

            if brand_id:
                # Fetch brand details
                url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/catalog/brands/{brand_id}"
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Auth-Token': store.access_token
                }
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    brand_data = response.json().get('data', {})
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Fetched brand details for BigCommerce brand ID {brand_id} (store {store.store_hash})",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
                    brand = store.env['bigcommerce.brand'].sudo().create({
                        'store_id': store.id,
                        'brand_id': brand_id,
                        'name': brand_data.get('name', f"Brand {brand_id}"),
                    })
                    _logger.info("Created brand %s for BigCommerce brand ID %s", brand.name, brand_id)
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Created brand {brand.name} for BigCommerce brand ID {brand_id} (store {store.store_hash})",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
                except requests.exceptions.RequestException as e:
                    error_msg = f"Failed to fetch brand {brand_id} for store {store.store_hash}: {str(e)}"
                    _logger.error(error_msg)
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Failed to fetch brand details for BigCommerce brand ID {brand_id}",
                        status='failure',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message=error_msg,
                        cr_user_id=request.uid
                    )
                    brand = store.env['bigcommerce.brand'].sudo().create({
                        'store_id': store.id,
                        'brand_id': brand_id,
                        'name': f"Brand {brand_id}",
                    })
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Created fallback brand Brand {brand_id} for BigCommerce brand ID {brand_id} (store {store.store_hash})",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
            else:
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"No brand ID provided for store {store.store_hash}, returning False",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return False

            _logger.info("Created store %s for BigCommerce brand ID %s", brand, brand.id)  # Retained original log
            return brand.id

        except Exception as e:
            error_msg = f"Error processing brand for BigCommerce brand ID {brand_id} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing brand for BigCommerce brand ID {brand_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise

    # before
    # def _get_or_create_partner(self, store, billing_address):
    #     """Get or create a partner based on billing address."""
    #     email = billing_address.get('email')
    #     if not email:
    #         raise ValidationError("Customer email missing in billing address")
    #
    #     partner = request.env['res.partner'].sudo().search([
    #         ('email', '=', email),
    #         ('bigcommerce_store_id', '=', store.id)
    #     ], limit=1)
    #
    #     if not partner:
    #         partner_vals = {
    #             'name': f"{billing_address.get('first_name', '')} {billing_address.get('last_name', '')}".strip(),
    #             'email': email,
    #             'bigcommerce_store_id': store.id,
    #             'bigcommerce_customer_id': billing_address.get('customer_id', 0),
    #             'bigcommerce_company': billing_address.get('company', ''),
    #             'street': billing_address.get('street_1', ''),
    #             'street2': billing_address.get('street_2', ''),
    #             'city': billing_address.get('city', ''),
    #             'zip': billing_address.get('zip', ''),
    #             'country_id': request.env['res.country'].sudo().search([('code', '=', billing_address.get('country_iso2', ''))], limit=1).id,
    #             'phone': billing_address.get('phone', ''),
    #             'bigcommerce_date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #             'bigcommerce_date_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #         }
    #         partner = request.env['res.partner'].sudo().create(partner_vals)
    #         _logger.info("Created partner %s for BigCommerce customer", partner.name)
    #
    #     return partner

    def _get_or_create_partner(self, store, billing_address):
        """Get or create a partner based on billing address."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        email = billing_address.get('email')
        if not email:
            error_msg = f"Customer email missing in billing address for store {store.store_hash}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process partner: Customer email missing",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise ValidationError("Customer email missing in billing address")

        try:
            partner = store.env['res.partner'].sudo().search([
                ('email', '=', email),
                ('bigcommerce_store_id', '=', store.id)
            ], limit=1)

            if partner:
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Found partner {partner.name} for email {email} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return partner

            partner_vals = {
                'name': f"{billing_address.get('first_name', '')} {billing_address.get('last_name', '')}".strip(),
                'email': email,
                'bigcommerce_store_id': store.id,
                'bigcommerce_customer_id': billing_address.get('customer_id', 0),
                'bigcommerce_company': billing_address.get('company', ''),
                'street': billing_address.get('street_1', ''),
                'street2': billing_address.get('street_2', ''),
                'city': billing_address.get('city', ''),
                'zip': billing_address.get('zip', ''),
                'country_id': store.env['res.country'].sudo().search(
                    [('code', '=', billing_address.get('country_iso2', ''))], limit=1).id,
                'phone': billing_address.get('phone', ''),
                'bigcommerce_date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'bigcommerce_date_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            partner = store.env['res.partner'].sudo().create(partner_vals)
            _logger.info("Created partner %s for BigCommerce customer", partner.name)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Created partner {partner.name} for BigCommerce customer with email {email} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return partner

        except Exception as e:
            error_msg = f"Error processing partner for email {email} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing partner for email {email}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise

    # before
    # def _get_or_create_order_status(self, store, status_id, name, custom_label):
    #     """Get or create BigCommerce order status."""
    #     status = request.env['bigcommerce.order.status'].sudo().search([
    #         ('store_id', '=', store.id),
    #         ('bigcommerce_status_id', '=', status_id)
    #     ], limit=1)
    #
    #     if not status:
    #         status_vals = {
    #             'store_id': store.id,
    #             'bigcommerce_status_id': status_id,
    #             'name': name or f"Status {status_id}",
    #             'custom_label': custom_label or name,
    #             'system_label': name,
    #             'order': status_id,
    #         }
    #         status = request.env['bigcommerce.order.status'].sudo().create(status_vals)
    #         _logger.info("Created order status %s for BigCommerce status ID %s", status.name, status_id)
    #
    #     return status

    def _get_or_create_order_status(self, store, status_id, name, custom_label):
        """Get or create BigCommerce order status."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            status = store.env['bigcommerce.order.status'].sudo().search([
                ('store_id', '=', store.id),
                ('bigcommerce_status_id', '=', status_id)
            ], limit=1)

            if status:
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Found order status {status.name} for BigCommerce status ID {status_id} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return status

            status_vals = {
                'store_id': store.id,
                'bigcommerce_status_id': status_id,
                'name': name or f"Status {status_id}",
                'custom_label': custom_label or name,
                'system_label': name,
                'order': status_id,
            }
            status = store.env['bigcommerce.order.status'].sudo().create(status_vals)
            _logger.info("Created order status %s for BigCommerce status ID %s", status.name, status_id)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Created order status {status.name} for BigCommerce status ID {status_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return status

        except Exception as e:
            error_msg = f"Error processing order status for BigCommerce status ID {status_id} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing order status for BigCommerce status ID {status_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise

    # before
    # def _prepare_order_lines(self, store, products):
    #     """Prepare order lines from BigCommerce products."""
    #     order_lines = []
    #     for product in products:
    #         odoo_product = request.env['product.product'].sudo().search([
    #             ('bigcommerce_product_id', '=', str(product.get('product_id')))
    #         ], limit=1)
    #         if not odoo_product:
    #             # Fetch product details to create a product
    #             product_data = self._fetch_product_details(store, product.get('product_id'))
    #             if product_data:
    #                 product_tmpl_vals = self._map_product_data(store, product_data)
    #                 product_tmpl = request.env['product.template'].sudo().create(product_tmpl_vals)
    #                 odoo_product = request.env['product.product'].sudo().create({
    #                     'product_tmpl_id': product_tmpl.id,
    #                     'bigcommerce_product_id': str(product_data.get('id')),
    #                     'bigcommerce_sku': product_data.get('sku', ''),
    #                     'bigcommerce_sku_id': product_data.get('variants', [{}])[0].get('id', 0),
    #                     'list_price': float(product_data.get('price', 0.0)),
    #                     'standard_price': float(product_data.get('cost_price', 0.0)),
    #                 })
    #             else:
    #                 odoo_product = request.env['product.product'].sudo().create({
    #                     'name': product.get('name', 'Unknown Product'),
    #                     'bigcommerce_product_id': str(product.get('product_id')),
    #                     'list_price': float(product.get('base_price', 0.0)),
    #                     'standard_price': float(product.get('base_price', 0.0)),
    #                     'bigcommerce_store_id': store.id,
    #                 })
    #
    #         line_vals = {
    #             'product_id': odoo_product.id,
    #             'product_uom_qty': product.get('quantity', 1),
    #             'price_unit': float(product.get('base_price', 0.0)),
    #             'name': product.get('name', ''),
    #             'tax_id': [(6, 0, self._get_tax_ids(store, product.get('tax', 0.0)))],
    #         }
    #         order_lines.append((0, 0, line_vals))
    #     return order_lines

    def _prepare_order_lines(self, store, products):
        """Prepare order lines from BigCommerce products."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        order_lines = []

        try:
            for product in products:
                product_id = product.get('product_id', 'unknown')
                odoo_product = store.env['product.product'].sudo().search([
                    ('bigcommerce_product_id', '=', str(product_id))
                ], limit=1)
                if odoo_product:
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Found Odoo product {odoo_product.name} for BigCommerce product ID {product_id} (store {store.store_hash})",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
                else:
                    # Fetch product details to create a product
                    product_data = self._fetch_product_details(store, product_id)
                    if product_data:
                        product_tmpl_vals = self._map_product_data(store, product_data)
                        product_tmpl = store.env['product.template'].sudo().create(product_tmpl_vals)
                        odoo_product = store.env['product.product'].sudo().create({
                            'product_tmpl_id': product_tmpl.id,
                            'bigcommerce_product_id': str(product_data.get('id')),
                            'bigcommerce_sku': product_data.get('sku', ''),
                            'bigcommerce_sku_id': product_data.get('variants', [{}])[0].get('id', 0),
                            'list_price': float(product_data.get('price', 0.0)),
                            'standard_price': float(product_data.get('cost_price', 0.0)),
                        })
                        store.env['cr.data.processing.log']._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Created Odoo product {odoo_product.name} for BigCommerce product ID {product_id} (store {store.store_hash})",
                            status='success',
                            timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            initiated_at=initiated_at,
                            error_message='',
                            cr_user_id=request.uid
                        )
                    else:
                        odoo_product = store.env['product.product'].sudo().create({
                            'name': product.get('name', 'Unknown Product'),
                            'bigcommerce_product_id': str(product_id),
                            'list_price': float(product.get('base_price', 0.0)),
                            'standard_price': float(product.get('base_price', 0.0)),
                            'bigcommerce_store_id': store.id,
                        })
                        store.env['cr.data.processing.log']._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Created fallback Odoo product {odoo_product.name} for BigCommerce product ID {product_id} (store {store.store_hash})",
                            status='success',
                            timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            initiated_at=initiated_at,
                            error_message='',
                            cr_user_id=request.uid
                        )

                line_vals = {
                    'product_id': odoo_product.id,
                    'product_uom_qty': product.get('quantity', 1),
                    'price_unit': float(product.get('base_price', 0.0)),
                    'name': product.get('name', ''),
                    'tax_id': [(6, 0, self._get_tax_ids(store, product.get('tax', 0.0)))],
                }
                order_lines.append((0, 0, line_vals))
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Prepared order line for product {odoo_product.name} (BigCommerce product ID {product_id}, store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )

            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Prepared {len(order_lines)} order lines for store {store.store_hash}",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return order_lines

        except Exception as e:
            error_msg = f"Error preparing order lines for store {store.store_hash}: {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Error preparing order lines",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise

    # before
    # def _get_tax_ids(self, store, tax_amount):
    #     """Map BigCommerce tax to Odoo tax (simplified)."""
    #     tax = request.env['account.tax'].sudo().search([
    #         ('amount', '=', float(tax_amount) * 100),  # Convert to percentage
    #         ('type_tax_use', '=', 'sale'),
    #         ('company_id', '=', self.company_id.id)
    #     ], limit=1)
    #     if not tax:
    #         tax = request.env['account.tax'].sudo().create({
    #             'name': f"BigCommerce Tax {tax_amount}",
    #             'amount': float(tax_amount) * 100,
    #             'type_tax_use': 'sale',
    #             'company_id': self.company_id.id,
    #         })
    #     return [tax.id]

    def _get_tax_ids(self, store, tax_amount):
        """Map BigCommerce tax to Odoo tax (simplified)."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            tax = store.env['account.tax'].sudo().search([
                ('amount', '=', float(tax_amount) * 100),  # Convert to percentage
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            if tax:
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Found tax {tax.name} for BigCommerce tax amount {tax_amount} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return [tax.id]

            tax = store.env['account.tax'].sudo().create({
                'name': f"BigCommerce Tax {tax_amount}",
                'amount': float(tax_amount) * 100,
                'type_tax_use': 'sale',
                'company_id': self.company_id.id,
            })
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Created tax BigCommerce Tax {tax_amount} for BigCommerce tax amount {tax_amount} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return [tax.id]

        except Exception as e:
            error_msg = f"Error mapping tax for BigCommerce tax amount {tax_amount} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error mapping tax for BigCommerce tax amount {tax_amount}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise

    # def _process_product_inventory_updated(self, store, data):
    #     """Process store/product/inventory/updated webhook: Update product inventory in Odoo for non-variant products."""
    #     product_id = data.get('id')
    #     inventory_data = data.get('inventory', {})
    #     if not product_id or not inventory_data:
    #         raise ValidationError("Product ID or inventory data missing in webhook data")

    #     # Validate inventory data
    #     method = inventory_data.get('method')
    #     value = inventory_data.get('value')
    #     if not method or value is None:
    #         raise ValidationError("Inventory method or value missing in webhook data")

    #     # Find product template
    #     product_tmpl = request.env['product.template'].sudo().search([
    #         ('bigcommerce_store_id', '=', store.id),
    #         ('bigcommerce_product_id', '=', str(product_id))
    #     ], limit=1)

    #     if not product_tmpl:
    #         _logger.warning("Product %s not found in Odoo", product_id)
    #         return

    #     # Check if product has exactly one variant (non-variant product)
    #     if len(product_tmpl.product_variant_ids) != 1:
    #         _logger.warning(
    #             "Product %s has multiple variants (%s) and is not managed by this webhook. Use variant-specific API.",
    #             product_id, len(product_tmpl.product_variant_ids))
    #         return

    #     # Get the single product variant
    #     product = product_tmpl.product_variant_id
    #     if not product:
    #         _logger.warning("No variant found for product %s", product_id)
    #         return

    #     # Get default warehouse and location
    #     warehouse = request.env['stock.warehouse'].sudo().search([('company_id', '=', request.env.user.company_id.id)], limit=1)
    #     if not warehouse:
    #         raise ValidationError("No warehouse found for the company")

    #     location = warehouse.lot_stock_id
    #     if not location:
    #         raise ValidationError("No stock location found for the warehouse")

    #     # Search for existing stock.quant record
    #     quant = request.env['stock.quant'].sudo().search([
    #         ('product_id', '=', product.id),
    #         ('location_id', '=', location.id),
    #     ], limit=1)

    #     # Use inventory_mode and system user (ID 2) for adjustments
    #     quant_env = request.env['stock.quant'].with_context(inventory_mode=True).with_user(2)

    #     if quant:
    #         # Update existing quant
    #         quant.with_user(2).write({'inventory_quantity': max(0, value)})  # Ensure non-negative quantity
    #         quant.with_user(2)._apply_inventory()
    #         _logger.info("Updated stock.quant for product %s (ID %s) in location %s with quantity %s (method: %s)",
    #                      product_tmpl.name, product_id, location.name, value, method)
    #     else:
    #         # Create new quant
    #         quant_env.with_user(2).create({
    #             'product_id': product.id,
    #             'location_id': location.id,
    #             'inventory_quantity': max(0, value),
    #         })._apply_inventory()
    #         _logger.info("Created stock.quant for product %s (ID %s) in location %s with quantity %s (method: %s)",
    #                      product_tmpl.name, product_id, location.name, value, method)

    #     # Update bigcommerce_inventory_level on product template
    #     product_tmpl.write({'bigcommerce_inventory_level': product.qty_available})


    # def _process_sku_inventory_updated(self, store, data):
    #     """Process store/sku/inventory/updated webhook: Update variant inventory in Odoo."""
    #     sku_id = data.get('id')
    #     inventory_data = data.get('inventory', {})
    #     product_id = inventory_data.get('product_id')
    #     variant_id = inventory_data.get('variant_id')

    #     if not (sku_id and product_id and variant_id and inventory_data):
    #         raise ValidationError("SKU ID, product ID, variant ID, or inventory data missing in webhook data")

    #     # Validate inventory data
    #     method = inventory_data.get('method')
    #     value = inventory_data.get('value')
    #     if not method or value is None:
    #         raise ValidationError("Inventory method or value missing in webhook data")

    #     # Find product variant by bigcommerce_sku_id (mapped to variant_id)
    #     product = request.env['product.product'].sudo().search([
    #         ('bigcommerce_store_id', '=', store.id),
    #         ('bigcommerce_sku_id', '=', sku_id),
    #         ('bigcommerce_product_id','=',product_id),
    #         ('bigcommerce_product_attribute_id','=',variant_id)
    #     ], limit=1)

    #     if not product:
    #         _logger.warning("Variant with SKU ID %s (variant ID %s, product ID %s) not found in Odoo",
    #                         sku_id, variant_id, product_id)
    #         return

    #     # Get default warehouse and location
    #     warehouse = request.env['stock.warehouse'].sudo().search([
    #         ('company_id', '=', request.env.user.company_id.id),
    #     ], limit=1)
    #     if not warehouse:
    #         raise ValidationError("No warehouse found for the company")

    #     location = warehouse.lot_stock_id
    #     if not location:
    #         raise ValidationError("No stock location found for the warehouse")

    #     # Search for existing stock.quant record
    #     quant = request.env['stock.quant'].sudo().search([
    #         ('product_id', '=', product.id),
    #         ('location_id', '=', location.id),
    #     ], limit=1)

    #     # Use inventory_mode and system user (ID 2) for adjustments
    #     quant_env = request.env['stock.quant'].with_context(inventory_mode=True).with_user(2)

    #     # Calculate new quantity based on method
    #     new_quantity = value if method == 'absolute' else (quant.quantity + value if quant else value)
    #     new_quantity = max(0, new_quantity)  # Ensure non-negative quantity

    #     if quant:
    #         # Update existing quant
    #         quant.with_user(2).write({'inventory_quantity': new_quantity})
    #         quant.with_user(2)._apply_inventory()
    #         _logger.info("Updated stock.quant for variant %s (SKU %s, product ID %s) in location %s with quantity %s (method: %s)",
    #                      product.name, sku_id, product_id, location.name, new_quantity, method)
    #     else:
    #         # Create new quant
    #         quant_env.with_user(2).create({
    #             'product_id': product.id,
    #             'location_id': location.id,
    #             'inventory_quantity': new_quantity,
    #         })._apply_inventory()
    #         _logger.info("Created stock.quant for variant %s (SKU %s, product ID %s) in location %s with quantity %s (method: %s)",
    #                      product.name, sku_id, product_id, location.name, new_quantity, method)

    #     # Update bigcommerce_inventory_level on product
    #     product.with_user(2).write({'bigcommerce_inventory_level': product.qty_available})





    # before
    # def _process_product_inventory_updated(self, store, data):
    #     """Process store/product/inventory/updated webhook: Update product inventory in Odoo for non-variant products."""
    #     product_id = data.get('id')
    #     inventory_data = data.get('inventory', {})
    #     if not product_id or not inventory_data:
    #         raise ValidationError("Product ID or inventory data missing in webhook data")
    #
    #     # Validate inventory data
    #     method = inventory_data.get('method')
    #     value = inventory_data.get('value')
    #     if not method or value is None:
    #         raise ValidationError("Inventory method or value missing in webhook data")
    #
    #     # Find product template
    #     product_tmpl = http.request.env['product.template'].sudo().search([
    #         ('bigcommerce_store_id', '=', store.id),
    #         ('bigcommerce_product_id', '=', str(product_id))
    #     ], limit=1)
    #
    #     if not product_tmpl:
    #         _logger.warning("Product %s not found in Odoo", product_id)
    #         return {'status': 'success', 'message': f'Product {product_id} not found'}
    #
    #     # Check if product has exactly one variant (non-variant product)
    #     if len(product_tmpl.product_variant_ids) != 1:
    #         _logger.warning(
    #             "Product %s has multiple variants (%s) and is not managed by this webhook. Use variant-specific API.",
    #             product_id, len(product_tmpl.product_variant_ids))
    #         return {'status': 'success', 'message': f'Product {product_id} has multiple variants'}
    #
    #     # Get the single product variant
    #     product = product_tmpl.product_variant_ids
    #     if not product:
    #         _logger.warning("No variant found for product %s", product_id)
    #         return {'status': 'success', 'message': f'No variant for product {product_id}'}
    #
    #     # Get default warehouse and location
    #     warehouse = http.request.env['stock.warehouse'].sudo().search(
    #         [('company_id', '=', http.request.env.user.company_id.id)], limit=1)
    #     if not warehouse:
    #         raise ValidationError("No warehouse found for the company")
    #
    #     location = warehouse.lot_stock_id
    #     if not location:
    #         raise ValidationError("No stock location found for the warehouse")
    #
    #     # Search for existing stock.quant record
    #     quant = http.request.env['stock.quant'].sudo().search([
    #         ('product_id', '=', product.id),
    #         ('location_id', '=', location.id),
    #     ], limit=1)
    #
    #     # Use inventory_mode and system user (ID 2) for adjustments
    #     quant_env = http.request.env['stock.quant'].with_context(inventory_mode=True).with_user(2)
    #
    #     if quant:
    #         # Update existing quant
    #         quant.with_user(2).write({'inventory_quantity': max(0, value)})
    #         quant.with_user(2)._apply_inventory()
    #         _logger.info("Updated stock.quant for product %s (ID %s) in location %s with quantity %s (method: %s)",
    #                      product_tmpl.name, product_id, location.name, value, method)
    #     else:
    #         # Create new quant
    #         quant_env.with_user(2).create({
    #             'product_id': product.id,
    #             'location_id': location.id,
    #             'inventory_quantity': max(0, value),
    #         })._apply_inventory()
    #         _logger.info("Created stock.quant for product %s (ID %s) in location %s with quantity %s (method: %s)",
    #                      product_tmpl.name, product_id, location.name, value, method)
    #
    #     return {'status': 'success', 'message': f'Inventory updated for product {product_id}'}

    def _process_product_inventory_updated(self, store, data):
        """Process store/product/inventory/updated webhook: Update product inventory in Odoo for non-variant products."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        product_id = data.get('id')
        inventory_data = data.get('inventory', {})

        if not product_id or not inventory_data:
            error_msg = f"Product ID or inventory data missing in webhook data for store {store.store_hash}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process inventory update: Product ID or inventory data missing",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise ValidationError("Product ID or inventory data missing in webhook data")

        # Validate inventory data
        method = inventory_data.get('method')
        value = inventory_data.get('value')
        if not method or value is None:
            error_msg = f"Inventory method or value missing in webhook data for product {product_id} (store {store.store_hash})"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process inventory update: Inventory method or value missing",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise ValidationError("Inventory method or value missing in webhook data")

        try:
            # Find product template
            product_tmpl = store.env['product.template'].sudo().search([
                ('bigcommerce_store_id', '=', store.id),
                ('bigcommerce_product_id', '=', str(product_id))
            ], limit=1)

            if not product_tmpl:
                _logger.warning("Product %s not found in Odoo", product_id)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product {product_id} not found in Odoo for inventory update (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return {'status': 'success', 'message': f'Product {product_id} not found'}

            # Check if product has exactly one variant (non-variant product)
            if len(product_tmpl.product_variant_ids) != 1:
                _logger.warning(
                    "Product %s has multiple variants (%s) and is not managed by this webhook. Use variant-specific API.",
                    product_id, len(product_tmpl.product_variant_ids))
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product {product_id} has {len(product_tmpl.product_variant_ids)} variants and is not managed by this webhook (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return {'status': 'success', 'message': f'Product {product_id} has multiple variants'}

            # Get the single product variant
            product = product_tmpl.product_variant_ids
            if not product:
                _logger.warning("No variant found for product %s", product_id)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"No variant found for product {product_id} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return {'status': 'success', 'message': f'No variant for product {product_id}'}

            # Get default warehouse and location
            warehouse = store.env['stock.warehouse'].sudo().search(
                [('company_id', '=', http.request.env.user.company_id.id)], limit=1)
            if not warehouse:
                error_msg = f"No warehouse found for company in store {store.store_hash}"
                _logger.error(error_msg)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message="Failed to process inventory update: No warehouse found",
                    status='failure',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid
                )
                raise ValidationError("No warehouse found for the company")

            location = warehouse.lot_stock_id
            if not location:
                error_msg = f"No stock location found for warehouse in store {store.store_hash}"
                _logger.error(error_msg)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message="Failed to process inventory update: No stock location found",
                    status='failure',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid
                )
                raise ValidationError("No stock location found for the warehouse")

            # Search for existing stock.quant record
            quant = store.env['stock.quant'].sudo().search([
                ('product_id', '=', product.id),
                ('location_id', '=', location.id),
            ], limit=1)

            # Use inventory_mode and system user (ID 2) for adjustments
            quant_env = store.env['stock.quant'].with_context(inventory_mode=True).with_user(2)

            if quant:
                # Update existing quant
                quant.with_user(2).write({'inventory_quantity': max(0, value)})
                quant.with_user(2)._apply_inventory()
                _logger.info("Updated stock.quant for product %s (ID %s) in location %s with quantity %s (method: %s)",
                             product_tmpl.name, product_id, location.name, value, method)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Updated stock for product {product_tmpl.name} (BigCommerce product ID {product_id}) with quantity {value} (method: {method}) in location {location.name} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
            else:
                # Create new quant
                quant_env.with_user(2).create({
                    'product_id': product.id,
                    'location_id': location.id,
                    'inventory_quantity': max(0, value),
                })._apply_inventory()
                _logger.info("Created stock.quant for product %s (ID %s) in location %s with quantity %s (method: %s)",
                             product_tmpl.name, product_id, location.name, value, method)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Created stock for product {product_tmpl.name} (BigCommerce product ID {product_id}) with quantity {value} (method: {method}) in location {location.name} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )

            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Inventory updated for BigCommerce product {product_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return {'status': 'success', 'message': f'Inventory updated for product {product_id}'}

        except Exception as e:
            error_msg = f"Error processing inventory update for product {product_id} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing inventory update for product {product_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            raise ValidationError(f"Error processing inventory update: {str(e)}")

    # before
    # def _process_sku_inventory_updated(self, store, data):
    #     """Process store/sku/inventory/updated webhook: Update variant inventory in Odoo."""
    #     sku_id = data.get('id')
    #     product_id = data['inventory']['product_id']
    #     variant_id = data['inventory']['variant_id']
    #     headers = {
    #             'Accept': 'application/json',
    #             'Content-Type': 'application/json',
    #             'X-Auth-Token': store.access_token
    #         }
    #
    #     if not (product_id and variant_id):
    #         _logger.error("Missing product ID or variant ID in webhook data: %s", data)
    #         return {'status': 'error', 'message': 'Missing product ID or variant ID'}
    #
    #     # Fetch all inventory locations
    #     locations_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations"
    #     try:
    #         response = requests.get(locations_url, headers=headers)
    #         response.raise_for_status()
    #         locations = response.json()['data']
    #         if not locations:
    #             _logger.warning("No locations found for store %s", store.store_hash)
    #             return {'status': 'success', 'message': 'No locations found'}
    #     except requests.exceptions.RequestException as e:
    #         _logger.error("Failed to fetch locations for store %s: %s", store.store_hash, str(e))
    #         return {'status': 'error', 'message': f'Failed to fetch locations: {str(e)}'}
    #
    #     # Find product variant
    #     product = http.request.env['product.product'].sudo().search([
    #         ('bigcommerce_store_id', '=', store.id),
    #         ('bigcommerce_product_id', '=', str(product_id)),
    #         ('bigcommerce_product_attribute_id', '=', str(variant_id))
    #     ], limit=1)
    #
    #     if not product:
    #         _logger.warning("Product not found for product ID %s, variant ID %s, store %s",
    #                         product_id, variant_id, store.store_hash)
    #         return {'status': 'success', 'message': f'Product not found for product {product_id}, variant {variant_id}'}
    #
    #     # Process inventory for each location
    #     found = False
    #     for location in locations:
    #         location_id = location['id']
    #         if not location['enabled']:
    #             _logger.info("Skipping disabled location %s for store %s", location_id, store.store_hash)
    #             continue
    #
    #         # Fetch inventory items for the location
    #         url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations/{location_id}/items"
    #         try:
    #             response = requests.get(url, headers=headers)
    #             response.raise_for_status()
    #             items = response.json()['data']
    #         except requests.exceptions.RequestException as e:
    #             _logger.warning("Failed to fetch inventory for location %s, store %s: %s",
    #                             location_id, store.store_hash, str(e))
    #             continue
    #
    #         # Find the item matching product_id and variant_id
    #         for item in items:
    #             identity = item['identity']
    #             if str(identity['product_id']) != str(product_id) or str(identity['variant_id']) != str(variant_id):
    #                 continue
    #
    #             found = True
    #             if not item['settings']['is_in_stock']:
    #                 _logger.info("Skipping out-of-stock item for SKU %s at location %s",
    #                              identity['sku'], location_id)
    #                 continue
    #
    #             # Find stock location
    #             stock_location = http.request.env['stock.location'].sudo().search([
    #                 ('bc_location_id', '=', str(location_id)),
    #                 ('bigcommerce_store_id', '=', store.id)
    #             ], limit=1)
    #
    #             if not stock_location:
    #                 _logger.warning("Stock location not found for location ID %s, store %s, SKU %s",
    #                                 location_id, store.store_hash, identity['sku'])
    #                 continue
    #
    #             # Update low stock threshold
    #             # product.write({
    #             #     'low_stock_threshold': item['settings']['warning_level']
    #             # })
    #
    #             # Update stock.quant
    #             quant = http.request.env['stock.quant'].sudo().search([
    #                 ('product_id', '=', product.id),
    #                 ('location_id', '=', stock_location.id)
    #             ], limit=1)
    #
    #             # Calculate quantity (available_to_sell - safety_stock, minimum 0)
    #             quantity = item['available_to_sell'] - item['settings']['safety_stock']
    #             quantity = max(0, quantity)
    #
    #             quant_env = http.request.env['stock.quant'].with_context(inventory_mode=True).with_user(2)
    #
    #             if quant:
    #                 quant.with_user(2).write({
    #                     'inventory_quantity': quantity,
    #                     'inventory_date': fields.Datetime.now()
    #                 })
    #                 quant.with_user(2)._apply_inventory()
    #                 _logger.info(
    #                     "Updated stock.quant for SKU %s (product ID %s, variant ID %s) at location %s with quantity %s",
    #                     identity['sku'], product_id, variant_id, stock_location.name, quantity)
    #             else:
    #                 quant_env.with_user(2).create({
    #                     'product_id': product.id,
    #                     'location_id': stock_location.id,
    #                     'inventory_quantity': quantity,
    #                     'inventory_date': fields.Datetime.now()
    #                 })._apply_inventory()
    #                 _logger.info(
    #                     "Created stock.quant for SKU %s (product ID %s, variant ID %s) at location %s with quantity %s",
    #                     identity['sku'], product_id, variant_id, stock_location.name, quantity)
    #
    #     if not found:
    #         _logger.warning("No inventory data found for product ID %s, variant ID %s, store %s",
    #                         product_id, variant_id, store.store_hash)
    #         return {'status': 'success', 'message': f'No inventory data for product {product_id}, variant {variant_id}'}
    #
    #     return {'status': 'success', 'message': f'Inventory updated for product {product_id}, variant {variant_id}'}

    def _process_sku_inventory_updated(self, store, data):
        """Process store/sku/inventory/updated webhook: Update variant inventory in Odoo."""
        # Initialize timestamp for logging
        initiated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sku_id = data.get('id')
        product_id = data.get('inventory', {}).get('product_id')
        variant_id = data.get('inventory', {}).get('variant_id')
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Auth-Token': store.access_token
        }

        if not (product_id and variant_id):
            error_msg = f"Missing product ID or variant ID in webhook data for store {store.store_hash}: {data}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message="Failed to process SKU inventory update: Missing product ID or variant ID",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            return {'status': 'error', 'message': 'Missing product ID or variant ID'}

        try:
            # Fetch all inventory locations
            locations_url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations"
            try:
                response = requests.get(locations_url, headers=headers)
                response.raise_for_status()
                locations = response.json()['data']
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Fetched {len(locations)} inventory locations for store {store.store_hash}",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                if not locations:
                    _logger.warning("No locations found for store %s", store.store_hash)
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"No locations found for store {store.store_hash}",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
                    return {'status': 'success', 'message': 'No locations found'}
            except requests.exceptions.RequestException as e:
                error_msg = f"Failed to fetch locations for store {store.store_hash}: {str(e)}"
                _logger.error(error_msg)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message="Failed to fetch inventory locations",
                    status='failure',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message=error_msg,
                    cr_user_id=request.uid
                )
                return {'status': 'error', 'message': f'Failed to fetch locations: {str(e)}'}

            # Find product variant
            product = store.env['product.product'].sudo().search([
                ('bigcommerce_store_id', '=', store.id),
                ('bigcommerce_product_id', '=', str(product_id)),
                ('bigcommerce_product_attribute_id', '=', str(variant_id))
            ], limit=1)

            if not product:
                _logger.warning("Product not found for product ID %s, variant ID %s, store %s",
                                product_id, variant_id, store.store_hash)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"Product not found for product ID {product_id}, variant ID {variant_id} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return {'status': 'success',
                        'message': f'Product not found for product {product_id}, variant {variant_id}'}

            # Process inventory for each location
            found = False
            for location in locations:
                location_id = location['id']
                if not location['enabled']:
                    _logger.info("Skipping disabled location %s for store %s", location_id, store.store_hash)
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Skipped disabled location {location_id} for store {store.store_hash}",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
                    continue

                # Fetch inventory items for the location
                url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/inventory/locations/{location_id}/items"
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    items = response.json()['data']
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Fetched {len(items)} inventory items for location {location_id} (store {store.store_hash})",
                        status='success',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message='',
                        cr_user_id=request.uid
                    )
                except requests.exceptions.RequestException as e:
                    _logger.warning("Failed to fetch inventory for location %s, store %s: %s",
                                    location_id, store.store_hash, str(e))
                    store.env['cr.data.processing.log']._log_data_processing(
                        cr_shop_id=store.id,
                        record_count=1,
                        cr_message=f"Failed to fetch inventory items for location {location_id} (store {store.store_hash})",
                        status='failure',
                        timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        initiated_at=initiated_at,
                        error_message=f"Failed to fetch inventory: {str(e)}",
                        cr_user_id=request.uid
                    )
                    continue

                # Find the item matching product_id and variant_id
                for item in items:
                    identity = item['identity']
                    if str(identity['product_id']) != str(product_id) or str(identity['variant_id']) != str(variant_id):
                        continue

                    found = True
                    if not item['settings']['is_in_stock']:
                        _logger.info("Skipping out-of-stock item for SKU %s at location %s",
                                     identity['sku'], location_id)
                        store.env['cr.data.processing.log']._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Skipped out-of-stock item for SKU {identity['sku']} at location {location_id} (store {store.store_hash})",
                            status='success',
                            timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            initiated_at=initiated_at,
                            error_message='',
                            cr_user_id=request.uid
                        )
                        continue

                    # Find stock location
                    stock_location = store.env['stock.location'].sudo().search([
                        ('bc_location_id', '=', str(location_id)),
                        ('bigcommerce_store_id', '=', store.id)
                    ], limit=1)

                    if not stock_location:
                        _logger.warning("Stock location not found for location ID %s, store %s, SKU %s",
                                        location_id, store.store_hash, identity['sku'])
                        store.env['cr.data.processing.log']._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Stock location not found for location ID {location_id}, SKU {identity['sku']} (store {store.store_hash})",
                            status='success',
                            timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            initiated_at=initiated_at,
                            error_message='',
                            cr_user_id=request.uid
                        )
                        continue

                    # Update low stock threshold (commented in original code)
                    # product.write({
                    #     'low_stock_threshold': item['settings']['warning_level']
                    # })

                    # Update stock.quant
                    quant = store.env['stock.quant'].sudo().search([
                        ('product_id', '=', product.id),
                        ('location_id', '=', stock_location.id)
                    ], limit=1)

                    # Calculate quantity (available_to_sell - safety_stock, minimum 0)
                    quantity = item['available_to_sell'] - item['settings']['safety_stock']
                    quantity = max(0, quantity)

                    quant_env = store.env['stock.quant'].with_context(inventory_mode=True).with_user(2)

                    if quant:
                        quant.with_user(2).write({
                            'inventory_quantity': quantity,
                            'inventory_date': fields.Datetime.now()
                        })
                        quant.with_user(2)._apply_inventory()
                        _logger.info(
                            "Updated stock.quant for SKU %s (product ID %s, variant ID %s) at location %s with quantity %s",
                            identity['sku'], product_id, variant_id, stock_location.name, quantity)
                        store.env['cr.data.processing.log']._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Updated stock for SKU {identity['sku']} (product ID {product_id}, variant ID {variant_id}) with quantity {quantity} at location {stock_location.name} (store {store.store_hash})",
                            status='success',
                            timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            initiated_at=initiated_at,
                            error_message='',
                            cr_user_id=request.uid
                        )
                    else:
                        quant_env.with_user(2).create({
                            'product_id': product.id,
                            'location_id': stock_location.id,
                            'inventory_quantity': quantity,
                            'inventory_date': fields.Datetime.now()
                        })._apply_inventory()
                        _logger.info(
                            "Created stock.quant for SKU %s (product ID %s, variant ID %s) at location %s with quantity %s",
                            identity['sku'], product_id, variant_id, stock_location.name, quantity)
                        store.env['cr.data.processing.log']._log_data_processing(
                            cr_shop_id=store.id,
                            record_count=1,
                            cr_message=f"Created stock for SKU {identity['sku']} (product ID {product_id}, variant ID {variant_id}) with quantity {quantity} at location {stock_location.name} (store {store.store_hash})",
                            status='success',
                            timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            initiated_at=initiated_at,
                            error_message='',
                            cr_user_id=request.uid
                        )

            if not found:
                _logger.warning("No inventory data found for product ID %s, variant ID %s, store %s",
                                product_id, variant_id, store.store_hash)
                store.env['cr.data.processing.log']._log_data_processing(
                    cr_shop_id=store.id,
                    record_count=1,
                    cr_message=f"No inventory data found for product ID {product_id}, variant ID {variant_id} (store {store.store_hash})",
                    status='success',
                    timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    initiated_at=initiated_at,
                    error_message='',
                    cr_user_id=request.uid
                )
                return {'status': 'success',
                        'message': f'No inventory data for product {product_id}, variant {variant_id}'}

            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Inventory updated for product ID {product_id}, variant ID {variant_id} (store {store.store_hash})",
                status='success',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message='',
                cr_user_id=request.uid
            )
            return {'status': 'success', 'message': f'Inventory updated for product {product_id}, variant {variant_id}'}

        except Exception as e:
            error_msg = f"Error processing SKU inventory update for product {product_id}, variant {variant_id} (store {store.store_hash}): {str(e)}"
            _logger.error(error_msg)
            store.env['cr.data.processing.log']._log_data_processing(
                cr_shop_id=store.id,
                record_count=1,
                cr_message=f"Error processing SKU inventory update for product ID {product_id}, variant ID {variant_id}",
                status='failure',
                timespan=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                initiated_at=initiated_at,
                error_message=error_msg,
                cr_user_id=request.uid
            )
            return {'status': 'error', 'message': f'Error processing SKU inventory update: {str(e)}'}