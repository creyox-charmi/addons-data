# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import http
from odoo.http import request
from odoo.addons.wb_portal_blogs.controllers.controllers import CustomerPortalBlogsController
from odoo.addons.http_routing.models.ir_http import slug, unslug
import base64, logging
import re
from odoo import exceptions, http
from odoo.http import request

_logger = logging.getLogger(__name__)

class TDPortalBlogController(CustomerPortalBlogsController):


    @http.route('/my/blog/get_terms', type='json', auth='user', methods=['POST'])
    def get_terms_condition(self):
        """Get terms and conditions for confirmation popup"""
        terms = request.env['terms.condition'].sudo().get_active_terms()
        if terms:
            return {
                'success': True,
                'title': terms.name,
                'description': terms.description
            }
        return {
            'success': False,
            'title': 'Terms and Conditions',
            'description': 'Please confirm that you agree to publish your data.'
        }

    @http.route('/my/blog/edit/<int:blog_id>', type='http', auth="user", website=True, csrf=True,
                methods=['GET', 'POST'])
    def portal_blog_edit_profile(self, blog_id, **kwargs):
        # If this is a POST request
        if request.httprequest.method == 'POST':
            is_published = kwargs.get('is_published') == '1'
            terms_confirmed = kwargs.get('terms_confirmed') == '1'

            # If user wants to publish but hasn't confirmed terms
            if is_published and not terms_confirmed:
                # Set is_published to False and continue with save
                kwargs['is_published'] = '0'
                # Call parent method with modified kwargs
                return super().portal_blog_edit_profile(blog_id, **kwargs)

            # If terms confirmed or not publishing, proceed normally
            if 'terms_confirmed' in kwargs:
                kwargs.pop('terms_confirmed')  # Remove confirmation flag

        # Call parent method for all other cases
        return super().portal_blog_edit_profile(blog_id, **kwargs)


    @http.route(['/my/messages/thread/partner/<int:partner_id>/blog/<int:blog_id>'], type='http', auth="user",
                website=True, csrf=True)
    def portal_messages_profile(self, partner_id, blog_id, **kwargs):
        values = {}
        try:
            blog_entry = partner = filtered_messages = None

            if blog_id and partner_id:
                blog_entry = request.env['blog.post'].sudo().browse(int(blog_id))
                partner = request.env['res.partner'].sudo().browse(int(partner_id))

            values = {
                'blog_entry': blog_entry,
                'partner': partner,
                'page_name': 'my_messages',
            }
        except Exception as exc:
            values.update({
                'error': True,
            })
        return request.render("wb_portal_blogs.portal_my_messages_form_view", values)

