# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import http
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class PortalSaleQuotation(http.Controller):

    @http.route('/portal_sale_quotation_tree', type='http', auth='user', website=True, csrf=False)
    def portal_sale_quotation_tree(self, **kw):
        customers = request.env['res.partner'].sudo().search([])
        products = request.env['product.template'].sudo().search([])
        uom = request.env['uom.uom'].sudo().search([])
        countries = request.env["res.country"].sudo().search([])
        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id", "in", countries.ids)])
        )
        return request.render('cr_portal_quote_and_rfq.portal_sale_quotation_tree', {
            'customers': customers,
            'products': products,
            'uom': uom,
            'countries': countries,
            'states': states,
        })

    @http.route(
        '/create_sale_order/success',
        auth="user",
        type="http",
        website=True,
        methods=["POST"],
        csrf=False
    )
    def create_sale_order(self, **post):
        """Create Sale Order — auto-create partner if needed."""

        partner_id = post.get('partner_id')
        product_template_ids = request.httprequest.form.getlist('product_ids[]')
        uom_ids = request.httprequest.form.getlist('uom_ids[]')
        prices = request.httprequest.form.getlist('prices[]')
        quantities = request.httprequest.form.getlist('quantities[]')

        # Basic validation
        if not product_template_ids:
            _logger.warning("Missing product_template_ids in POST data")
            return request.redirect('/portal_sale_quotation_tree')

        # Handle partner (existing or new)
        partner = None
        if partner_id and str(partner_id).isdigit():
            partner = request.env['res.partner'].sudo().browse(int(partner_id))
            if not partner.exists():
                partner = None
        if not partner:
            # Create new customer using POST data or fallback to current user
            partner_vals = {
                'name': post.get('partner_name') or request.env.user.name or 'New Customer',
                'email': post.get('partner_email') or request.env.user.email,
                'phone': post.get('partner_phone'),
            }
            partner = request.env['res.partner'].sudo().create(partner_vals)
            _logger.info(f"Created new partner {partner.name} (ID: {partner.id})")

        # Use sudo for backend operations
        SaleOrder = request.env['sale.order'].sudo()
        SaleOrderLine = request.env['sale.order.line'].sudo()
        ProductProduct = request.env['product.product'].sudo()
        ProductTemplate = request.env['product.template'].sudo()

        # Create Sale Order
        sale_order = SaleOrder.create({'partner_id': partner.id})
        _logger.info(f"Created Sale Order {sale_order.name} for partner {partner.name}")

        # Create Sale Order Lines
        for i in range(len(product_template_ids)):
            try:
                product_template_id = int(product_template_ids[i])
                product_template = ProductTemplate.browse(product_template_id)

                # Check if the line contains valid data
                product_id = product_template_ids[i]
                uom_id = uom_ids[i]
                price = prices[i]
                quantity = quantities[i]

                if product_id == '-- Select a Product --' or uom_id == '-- Select a UOM --' or price == 'NaN' or quantity == 'NaN':
                    # Skip this line if any of the conditions are met
                    continue

                if not product_template.exists():
                    _logger.warning(f"Product Template ID {product_template_id} not found.")
                    continue

                # Find corresponding product variant
                product = ProductProduct.search(
                    [('product_tmpl_id', '=', product_template.id)],
                    limit=1
                )
                if not product:
                    _logger.warning(f"No variant found for template {product_template.id}")
                    continue

                SaleOrderLine.create({
                    'order_id': sale_order.id,
                    'product_template_id': product_template.id,
                    'product_id': product.id,
                    'name': product_template.name or 'Product Description',
                    'product_uom_qty': float(quantity),
                    'price_unit': float(price),
                    'product_uom': int(uom_id),
                })
            except Exception as e:
                _logger.error(f"Error creating sale order line: {e}")
                continue

        # Send quotation email
        try:
            template = request.env.ref('sale.email_template_edi_sale', raise_if_not_found=False)
            if template:
                template.sudo().send_mail(sale_order.id, force_send=True)
        except Exception as e:
            _logger.error(f"Failed to send quotation email: {e}")

        # Set state to 'sent'
        sale_order.sudo().write({'state': 'sent'})

        # Store last sale order in session
        request.session['last_created_sale_order_id'] = sale_order.id
        request.session['last_created_partner_id'] = partner.id

        _logger.info(f"Sale order {sale_order.name} created successfully for {partner.name} (ID: {partner.id})")

        return request.redirect('/create_sale_order/success/page')

    @http.route('/create_sale_order/success/page', auth="user", type="http", website=True)
    def show_sale_order_success(self, **kwargs):
        order_id = request.session.get('last_created_sale_order_id')
        if not order_id:
            return request.redirect('/portal_sale_quotation_tree')

        sale_order = request.env['sale.order'].sudo().browse(order_id)
        if not sale_order.exists():
            return request.redirect('/portal_sale_quotation_tree')

        website = request.env['website'].get_current_website()
        return request.render('cr_portal_quote_and_rfq.sale_generated_success_template', {
            'sale_order': sale_order,
            'website': website,
        })

    @http.route('/portal_purchase_rfq_tree', type='http', auth='user', website=True, csrf=False)
    def portal_purchase_rfq_tree(self, **kw):
        customers = request.env['res.partner'].sudo().search([])
        products = request.env['product.product'].sudo().search([])
        countries = request.env["res.country"].sudo().search([])
        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id", "in", countries.ids)])
        )
        return request.render('cr_portal_quote_and_rfq.portal_purchase_rfq_tree', {
            'customers': customers,
            'products': products,
            'countries': countries,
            'states': states,
        })

    @http.route('/create_purchase_rfq/success', auth="user", type="http", website=True, methods=["POST"], csrf=False)
    def create_purchase_rfq(self, **post):
        """Create Purchase Order — auto-create partner if needed."""

        partner_id = post.get('partner_id')
        product_ids = request.httprequest.form.getlist('product_ids[]')
        prices = request.httprequest.form.getlist('prices[]')
        quantities = request.httprequest.form.getlist('quantities[]')

        # Basic validation
        if not partner_id or not product_ids:
            _logger.warning("Missing partner_id or product_ids in POST data")
            return request.redirect('/portal_purchase_rfq_tree')

        # Handle partner (existing or new)
        partner = None
        if partner_id and str(partner_id).isdigit():
            partner = request.env['res.partner'].sudo().browse(int(partner_id))
            if not partner.exists():
                partner = None

        if not partner:
            # Create new partner if not found
            partner_vals = {
                'name': post.get('partner_name') or request.env.user.name or 'New Supplier',
                'email': post.get('partner_email') or request.env.user.email,
                'phone': post.get('partner_phone'),
            }
            partner = request.env['res.partner'].sudo().create(partner_vals)
            _logger.info(f"Created new partner {partner.name} (ID: {partner.id})")

        # Use sudo for backend operations
        PurchaseOrder = request.env['purchase.order'].sudo()
        PurchaseOrderLine = request.env['purchase.order.line'].sudo()
        ProductProduct = request.env['product.product'].sudo()
        ProductTemplate = request.env['product.template'].sudo()

        # Create the Purchase Order
        purchase_order = PurchaseOrder.create({'partner_id': partner.id})
        _logger.info(f"Created Purchase Order {purchase_order.name} for partner {partner.name}")

        # Create Purchase Order Lines
        for i in range(len(product_ids)):
            try:
                product_id = int(product_ids[i])
                product = ProductProduct.browse(product_id)

                # Check if the line contains valid data
                price = prices[i]
                quantity = quantities[i]

                if product_id == '-- Select a Product --' or price == 'NaN' or quantity == 'NaN':
                    # Skip this line if any condition is met
                    continue

                if not product.exists():
                    _logger.warning(f"Product ID {product_id} not found.")
                    continue

                PurchaseOrderLine.create({
                    'order_id': purchase_order.id,
                    'product_id': product.id,
                    'name': product.name or 'Product Description',
                    'product_uom_qty': float(quantity),
                    'price_unit': float(price),
                })
            except Exception as e:
                _logger.error(f"Error creating purchase order line: {e}")
                continue

        # Send RFQ email using template
        try:
            template = request.env.ref('purchase.email_template_edi_purchase', raise_if_not_found=False)
            if template:
                template.sudo().send_mail(purchase_order.id, force_send=True)
        except Exception as e:
            _logger.error(f"Failed to send RFQ email: {e}")

        # Set purchase order state to 'sent'
        purchase_order.sudo().write({'state': 'sent'})

        # Store last created purchase order in session
        request.session['last_created_purchase_order_id'] = purchase_order.id
        request.session['last_created_partner_id'] = partner.id

        _logger.info(f"Purchase order {purchase_order.name} created successfully for {partner.name} (ID: {partner.id})")

        return request.redirect('/create_purchase_rfq/success/page')

    @http.route('/create_purchase_rfq/success/page', auth="user", type="http", website=True)
    def show_purchase_order_success(self, **kwargs):
        order_id = request.session.get('last_created_purchase_order_id')
        if not order_id:
            return request.redirect('/portal_purchase_rfq_tree')

        purchase_order = request.env['purchase.order'].sudo().browse(order_id)
        if not purchase_order.exists():
            return request.redirect('/portal_purchase_rfq_tree')

        website = request.env['website'].get_current_website()
        return request.render('cr_portal_quote_and_rfq.purchase_generated_success_template', {
            'purchase_order': purchase_order,
            'website': website,
        })

    # @http.route('/create_customer', type='http', auth='user', methods=['POST'], csrf=False)
    # def create_customer(self, **post):
    #     customer_name = post.get('customer_name', '').strip()
    #     customer_phone = post.get('customer_phone', '').strip()
    #     customer_email = post.get('customer_email', '').strip()
    #     street = post.get('street', '').strip()
    #     street2 = post.get('street2', '').strip()
    #     city = post.get('city', '').strip()
    #     zip_code = post.get('zip', '').strip()
    #     state_id = post.get('state')
    #     country_id = post.get('country')
    #
    #     if not customer_name:
    #         return """
    #                         <script>
    #                             alert("Customer name is required.");
    #                             window.history.back();
    #                         </script>
    #                     """
    #
    #     try:
    #         # Prepare customer data
    #         customer_data = {
    #             'name': customer_name,
    #             'is_company': False,
    #             'phone': customer_phone or False,
    #             'email': customer_email or False,
    #             'street': street or False,
    #             'street2': street2 or False,
    #             'city': city or False,
    #             'zip': zip_code or False,
    #         }
    #         if state_id:
    #             customer_data['state_id'] = int(state_id)
    #         if country_id:
    #             customer_data['country_id'] = int(country_id)
    #
    #         # Create new customer
    #         customer = request.env['res.partner'].sudo().create(customer_data)
    #         return f"""
    #                         <script>
    #                             alert("Customer '{customer.name}' created successfully!");
    #                             window.history.back();
    #                         </script>
    #                     """
    #     except Exception as e:
    #         return f"""
    #                         <script>
    #                             alert("Failed to create customer: {str(e)}");
    #                             window.history.back();
    #                         </script>
    #                     """

    @http.route('/create_customer', type='http', auth='user', methods=['POST'], csrf=False, website=True)
    def create_customer(self, **post):
        """Create a new customer and return JSON response"""
        customer_name = post.get('customer_name', '').strip()
        customer_phone = post.get('customer_phone', '').strip()
        customer_email = post.get('customer_email', '').strip()
        street = post.get('street', '').strip()
        street2 = post.get('street2', '').strip()
        city = post.get('city', '').strip()
        zip_code = post.get('zip', '').strip()
        state_id = post.get('states')  # Note: your form uses 'states' not 'state'
        country_id = post.get('countries')  # Note: your form uses 'countries' not 'country'

        if not customer_name:
            return Response(
                json.dumps({
                    'success': False,
                    'error': 'Customer name is required.'
                }),
                content_type='application/json',
                status=400
            )

        try:
            # Prepare customer data
            customer_data = {
                'name': customer_name,
                'is_company': False,
                'customer_rank': 1,  # Mark as customer
                'phone': customer_phone or False,
                'email': customer_email or False,
                'street': street or False,
                'street2': street2 or False,
                'city': city or False,
                'zip': zip_code or False,
            }

            if state_id and state_id.isdigit():
                customer_data['state_id'] = int(state_id)
            if country_id and country_id.isdigit():
                customer_data['country_id'] = int(country_id)

            # Create new customer
            customer = request.env['res.partner'].sudo().create(customer_data)

            _logger.info(f"Customer created: {customer.name} (ID: {customer.id})")

            # Return JSON response
            return Response(
                json.dumps({
                    'success': True,
                    'customer_id': customer.id,
                    'customer_name': customer.name,
                    'message': f"Customer '{customer.name}' created successfully!"
                }),
                content_type='application/json',
                status=200
            )

        except Exception as e:
            _logger.error(f"Failed to create customer: {str(e)}")
            return Response(
                json.dumps({
                    'success': False,
                    'error': f"Failed to create customer: {str(e)}"
                }),
                content_type='application/json',
                status=500
            )