# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import requests
import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bigcommerce_store_id = fields.Many2one('bigcommerce.store', string="BigCommerce Store")
    bigcommerce_order_id = fields.Integer("BigCommerce Order ID", readonly=True)
    bigcommerce_order_status_id = fields.Many2one(
        'bigcommerce.order.status',
        string="BigCommerce Order Status"
    )
    bigcommerce_subtotal_ex_tax = fields.Float("Subtotal Excl. Tax", readonly=True)
    bigcommerce_subtotal_inc_tax = fields.Float("Subtotal Incl. Tax", readonly=True)
    bigcommerce_subtotal_tax = fields.Float("Subtotal Tax", readonly=True)
    bigcommerce_base_shipping_cost = fields.Float("Base Shipping Cost", readonly=True)
    bigcommerce_shipping_cost_ex_tax = fields.Float("Shipping Cost Excl. Tax", readonly=True)
    bigcommerce_shipping_cost_inc_tax = fields.Float("Shipping Cost Incl. Tax", readonly=True)
    bigcommerce_total_ex_tax = fields.Float("Total Excl. Tax", readonly=True)
    bigcommerce_total_inc_tax = fields.Float("Total Incl. Tax", readonly=True)
    bigcommerce_total_tax = fields.Float("Total Tax", readonly=True)
    bigcommerce_payment_method = fields.Char("Payment Method", readonly=True)
    bigcommerce_payment_status = fields.Char("Payment Status", readonly=True)
    bigcommerce_refunded_amount = fields.Float("Refunded Amount", readonly=True)
    bigcommerce_discount_amount = fields.Float("Discount Amount", readonly=True)
    bigcommerce_customer_message = fields.Text("Customer Message", readonly=True)
    bigcommerce_staff_notes = fields.Text("Staff Notes", readonly=True)

    def action_get_bigcommerce_order_status(self):
        for order in self:
            if not order.bigcommerce_store_id:
                raise UserError(_("BigCommerce store not linked to this order."))

            if not order.bigcommerce_order_status_id:
                raise UserError(_("This order does not yet have a BigCommerce status."))

            store = order.bigcommerce_store_id
            status_id = order.bigcommerce_order_status_id.bigcommerce_status_id

            headers = {
                "X-Auth-Token": store.access_token,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/order_statuses/{status_id}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise UserError(_("Failed to fetch order status from BigCommerce: %s") % response.text)

            new_status = response.json()

            # Find or create the new status record
            status_obj = self.env['bigcommerce.order.status'].search([
                ('bigcommerce_status_id', '=', new_status['id']),
                ('store_id', '=', store.id)
            ], limit=1)

            if not status_obj:
                status_obj = self.env['bigcommerce.order.status'].create({
                    'status_id': new_status['id'],
                    'name': new_status['name'],
                    'system_label': new_status['system_label'],
                    'custom_label': new_status['custom_label'],
                    'system_description': new_status['system_description'],
                    'order': new_status['order'],
                    'store_id': store.id,
                })

            if order.bigcommerce_order_status_id != status_obj:
                order.bigcommerce_order_status_id = status_obj

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Order Status Synced"),
                'message': _("Order status was successfully fetched and updated."),
                'sticky': False,
            }
        }

    # def action_update_bigcommerce_order(self):
    #     for order in self:
    #         if not order.bigcommerce_store_id or not order.bigcommerce_order_id:
    #             raise UserError(_("Missing BigCommerce Store or Order ID."))
    #
    #         store = order.bigcommerce_store_id
    #
    #         url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order.bigcommerce_order_id}"
    #         headers = {
    #             'X-Auth-Token': store.access_token,
    #             'Accept': 'application/json',
    #             'Content-Type': 'application/json'
    #         }
    #
    #         payload = {
    #             "status_id": order.bigcommerce_order_status_id.external_status_id or 0,
    #             "staff_notes": order.note or "Updated via Odoo",
    #             "subtotal_ex_tax": str(order.amount_untaxed),
    #             "subtotal_inc_tax": str(order.amount_total),
    #             "total_ex_tax": str(order.amount_untaxed),
    #             "total_inc_tax": str(order.amount_total),
    #             "discount_amount": str(order.amount_discount if hasattr(order, 'amount_discount') else "0.00"),
    #             "shipping_cost_ex_tax": "0.0000",
    #             "shipping_cost_inc_tax": "0.0000",
    #             "handling_cost_ex_tax": "0.0000",
    #             "handling_cost_inc_tax": "0.0000",
    #             "wrapping_cost_ex_tax": "0.0000",
    #             "wrapping_cost_inc_tax": "0.0000",
    #             "order_is_digital": all(l.product_id.type == 'service' for l in order.order_line),
    #             "items_total": len(order.order_line),
    #             "items_shipped": sum(l.qty_delivered for l in order.order_line),
    #             "payment_method": order.payment_term_id.name if order.payment_term_id else "Manual",
    #         }
    #
    #         response = requests.put(url, headers=headers, json=payload)
    #
    #         if response.status_code != 200:
    #             raise UserError(_(
    #                 "Failed to update order in BigCommerce:\n%s - %s"
    #             ) % (response.status_code, response.text))
    #
    #         # ✅ Success toast notification using 'display_notification'
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'type': 'success',
    #                 'title': _("Order Synced"),
    #                 'message': _("Order was successfully updated in BigCommerce."),
    #                 'sticky': False,
    #             }
    #         }
    #     return None

    def action_update_bigcommerce_order(self):
        for order in self:
            if not order.bigcommerce_store_id or not order.bigcommerce_order_id:
                raise UserError(_("Missing BigCommerce Store or Order ID."))

            store = order.bigcommerce_store_id
            headers = {
                'X-Auth-Token': store.access_token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            # 1. Get existing products from BigCommerce
            url_products = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order.bigcommerce_order_id}/products"
            response = requests.get(url_products, headers=headers)
            if response.status_code != 200:
                raise UserError(_("Failed to fetch BigCommerce order products:\n%s") % response.text)
            bc_products = response.json()

            def product_key(p):
                opts = tuple(
                    (opt['id'], opt['value']) for opt in p.get('product_options', [])) if 'product_options' in p else ()
                return (p.get('product_id'), opts)

            bc_products_map = {product_key(p): p for p in bc_products}
            products_payload = []

            # 2. Compare Odoo lines with BigCommerce order lines
            for line in order.order_line:
                variant_opts = []
                for ptav in line.product_id.product_template_attribute_value_ids:
                    val = ptav.product_attribute_value_id
                    option_id = val.attribute_id.bigcommerce_option_id
                    value_id = val.bigcommerce_value_id
                    if option_id and value_id:
                        variant_opts.append((option_id, value_id))

                key = (line.product_id.bigcommerce_product_id, tuple(sorted(variant_opts)))
                bc_product = bc_products_map.get(key)

                if bc_product:
                    qty_differs = bc_product['quantity'] != int(line.product_uom_qty)
                    price_differs = float(bc_product.get('price_inc_tax', 0)) != float(line.price_unit)

                    if qty_differs or price_differs:
                        product_data = {
                            "product_id": line.product_id.bigcommerce_product_id,
                            "quantity": int(line.product_uom_qty),
                            "price_inc_tax": line.price_unit,
                            "price_ex_tax": line.price_unit,
                        }
                        if variant_opts:
                            product_data["product_options"] = [{"id": o, "value": v} for o, v in variant_opts]
                        products_payload.append(product_data)

                    bc_products_map.pop(key)
                else:
                    # Product not in BC, add it
                    product_data = {
                        "name": line.name,
                        "sku": line.product_id.default_code or "",
                        "quantity": int(line.product_uom_qty),
                        "price_inc_tax": line.price_unit,
                        "price_ex_tax": line.price_unit,
                    }
                    if variant_opts:
                        product_data["product_options"] = [{"id": o, "value": v} for o, v in variant_opts]
                    products_payload.append(product_data)

            # 3. Products to remove (present in BC but not in Odoo)
            for bc_p in bc_products_map.values():
                products_payload.append({
                    "id": bc_p['id'],
                    "product_id": bc_p['product_id'],
                    "quantity": 0  # Quantity 0 to remove
                })

            # 4. Order metadata
            payload = {
                "status_id": order.bigcommerce_order_status_id.bigcommerce_status_id or 0,
                "staff_notes": order.note or "Updated via Odoo",
                "subtotal_ex_tax": str(order.amount_untaxed),
                "subtotal_inc_tax": str(order.amount_total),
                "total_ex_tax": str(order.amount_untaxed),
                "total_inc_tax": str(order.amount_total),
                "discount_amount": str(order.amount_discount if hasattr(order, 'amount_discount') else "0.00"),
                "shipping_cost_ex_tax": "0.0000",
                "shipping_cost_inc_tax": "0.0000",
                "handling_cost_ex_tax": "0.0000",
                "handling_cost_inc_tax": "0.0000",
                "wrapping_cost_ex_tax": "0.0000",
                "wrapping_cost_inc_tax": "0.0000",
                "order_is_digital": all(l.product_id.type == 'service' for l in order.order_line),
                "items_total": len(order.order_line),
                "items_shipped": sum(l.qty_delivered for l in order.order_line),
                "payment_method": order.payment_term_id.name if order.payment_term_id else "Manual",
            }

            if products_payload:
                payload["products"] = products_payload

            # 5. PUT to BigCommerce
            url_order = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order.bigcommerce_order_id}"
            resp = requests.put(url_order, headers=headers, json=payload)
            if resp.status_code != 200:
                raise UserError(_("Failed to update order in BigCommerce:\n%s - %s") % (resp.status_code, resp.text))

            # 6. Success notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': _("Order Synced"),
                    'message': _("Order was successfully updated in BigCommerce."),
                    'sticky': False,
                }
            }
        return None

    def action_import_bigcommerce_order(self):
        for order in self:
            if not order.bigcommerce_store_id or not order.bigcommerce_order_id:
                raise UserError(_("Missing BigCommerce Store or Order ID."))

            store = order.bigcommerce_store_id
            headers = {
                'X-Auth-Token': store.access_token,
                'Accept': 'application/json'
            }

            url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order.bigcommerce_order_id}?include=fees"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise UserError(_("Failed to fetch BigCommerce order:\n%s") % response.text)

            bc_order = response.json()

            # Update order-level fields
            order.write({
                'partner_id': self.env['res.partner']._find_or_create_from_bigcommerce(bc_order['billing_address']),
                'amount_total': bc_order['total_inc_tax'],
                'amount_untaxed': bc_order['total_ex_tax'],
                'note': bc_order.get('staff_notes', ''),
                'bigcommerce_order_status_id': self.env['bigcommerce.order.status'].search(
                    [('external_status_id', '=', bc_order['status_id'])], limit=1).id,
            })

            # Clear existing lines
            order.order_line.unlink()

            # Fetch products from BC (separate endpoint)
            url_products = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/orders/{order.bigcommerce_order_id}/products"
            resp_products = requests.get(url_products, headers=headers)
            if resp_products.status_code != 200:
                raise UserError(_("Failed to fetch products for order:\n%s") % resp_products.text)

            for p in resp_products.json():
                product = self.env['product.product'].search([('bigcommerce_product_id', '=', p['product_id'])],
                                                             limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'name': p['name'],
                        'default_code': p.get('sku'),
                        'bigcommerce_product_id': p['product_id'],
                        'lst_price': p.get('price_inc_tax') or p.get('price_ex_tax'),
                    })

                order.order_line.create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'name': p['name'],
                    'product_uom_qty': p['quantity'],
                    'price_unit': float(p.get('price_inc_tax') or p.get('price_ex_tax') or 0),
                })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Order Synced"),
                'message': _("Order has been successfully updated from BigCommerce."),
                'sticky': False,
            }
        }

    def action_bulk_update_bigcommerce_order(self):
        for order in self:
            try:
                order.action_update_bigcommerce_order()
            except Exception as e:
                _logger.exception("Failed to update BigCommerce order %s: %s", order.name, str(e))
                raise UserError(_("Failed to update BigCommerce order %s: %s") % (order.name, str(e)))

    def action_bulk_import_bigcommerce_order(self):
        for order in self:
            try:
                order.action_import_bigcommerce_order()
            except Exception as e:
                _logger.exception("Failed to import BigCommerce order %s: %s", order.name, str(e))
                raise UserError(_("Failed to import BigCommerce order %s: %s") % (order.name, str(e)))

    def _set_delivery_cost(self, carrier, amount):
        self.ensure_one()
        if not carrier.product_id:
            _logger.warning("No delivery product configured for carrier %s on order %s", carrier.name, self.name)
            return False

        delivery_lines = self.order_line.filtered(lambda l: l.is_delivery)
        if delivery_lines:
            delivery_lines.unlink()
        taxes = carrier.product_id.taxes_id
        self.env['sale.order.line'].create({
            'order_id': self.id,
            'product_id': carrier.product_id.id,
            'price_unit': amount,
            'product_uom_qty': 1,
            'is_delivery': True,
            'tax_id': [(6, 0, taxes.ids)],
        })

        self.carrier_id = carrier.id
        self._compute_amounts()
        return True

    def _action_create_delivery(self):
        self.ensure_one()
        if not self.order_line:
            return False
        delivery_wizard = self.env['stock.immediate.transfer'].create({
            'pick_to_backorder': False,
            'picking_ids': [(6, 0, [])],
        })
        delivery_wizard.with_context(active_ids=self.ids).action_create_delivery()
        return True
