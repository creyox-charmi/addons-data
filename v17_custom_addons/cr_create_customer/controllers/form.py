from odoo import http, SUPERUSER_ID, _, _lt
from odoo.http import request


class WebsiteForm(http.Controller):
    @http.route(['/user/form'], type='http', auth='public', website='True')
    def user_form(self, **post):
        country_state_ids = request.env['res.country.state'].sudo().search([])
        country_ids = request.env['res.country'].sudo().search([])
        product_ids = request.env['product.product'].sudo().search([])
        vals = {}
        vals = {
            'state_id': country_state_ids,
            'country_id': country_ids,
            'product_ids':product_ids
        }
        return request.render("cr_create_customer.user_registration_form_template", vals)

    @http.route(['/user/form/submit'], type='http', auth='public', website='True')
    def user_form_submit(self, **post):

        user_dict = {}
        user_dict = {
                    'first_name': post.get('first_name'),
                    'last_name': post.get('last_name'),
                    'email': post.get('email'),
                    'phone_no': post.get('mobile'),
                    'country_id': post.get('country_id'),
                    'state_id': post.get('state_id'),
                    'city': post.get('city'),
                    'zip': post.get('zip'),
                    'address': post.get('address'),
                    }


        if user_dict:
            request.env['cr.customer'].sudo().create(user_dict)
        return request.render("cr_create_customer.user_registration_form_success_template")





