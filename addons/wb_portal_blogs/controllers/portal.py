# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager


class CustomerPortalBlogs(CustomerPortal):

    def _get_blogs_domain(self, partner_id):
        return [
            '|', '|',
            ('author_id', 'in', [partner_id, SUPERUSER_ID]),
            ('create_uid', 'in', [partner_id, SUPERUSER_ID]),
            ('write_uid', 'in', [partner_id, SUPERUSER_ID])
        ]

    def _prepare_home_portal_values(self, counters):
        """ Add subscription details to main account page """
        values = super()._prepare_home_portal_values(counters)
        if 'blogs_count' in counters:
            #     if request.env['sale.order'].check_access_rights('read', raise_exception=False):
            partner = request.env.user.partner_id.id
            BlogPost = request.env['blog.post'].sudo()
            blog_blog_id = BlogPost.blog_id.search([('name', 'ilike', 'comunidad')], limit=1)
            values['blogs_count'] = len(
                request.env['blog.post'].sudo().search(self._get_blogs_domain(partner)).filtered(
                    lambda x: x.blog_id.id == blog_blog_id.id
                )
            )
        if 'message_count' in counters:
            partner = request.env.user.partner_id.id
            BlogPost = request.env['blog.post'].sudo()
            blog_blog_id = BlogPost.blog_id.search([('name', 'ilike', 'comunidad')], limit=1)
            blog_post_ids = request.env['blog.post'].sudo().search(self._get_blogs_domain(partner)).filtered(
                lambda x: x.blog_id.id == blog_blog_id.id
            )

            values['message_count'] = len(
                blog_post_ids.message_ids
            )
        return values
