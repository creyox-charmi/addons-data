# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.mail import PortalChatter, _check_special_access
from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.addons.http_routing.models.ir_http import slug, unslug


class CommunityBlogPortalChatter(PortalChatter):

    @http.route('/mail/chatter_fetch', type='json', auth='public', website=True)
    def portal_message_fetch(self, res_model, res_id, domain=False, limit=10, offset=0, **kw):
        """Override to filter messages for community blog posts"""

        # Check if this is a blog post in community blog
        if res_model == 'blog.post':
            blog_post = request.env['blog.post'].sudo().browse(int(res_id))

            community_blog = request.env['blog.blog'].sudo().search([('name', 'ilike', 'comunidad')], limit=1)

            is_community_blog = blog_post.exists() and community_blog and blog_post.blog_id.id == community_blog.id

            if is_community_blog:
                user = request.env.user

                is_post_author = blog_post.author_id.id == user.partner_id.id if user.partner_id else False

                # Build domain similar to parent method
                model = request.env[res_model]
                field = model._fields['website_message_ids']
                field_domain = field.get_domain_list(model)

                base_domain = expression.AND([
                    self._setup_portal_message_fetch_extra_domain(kw),
                    field_domain,
                    [('res_id', '=', res_id), '|', ('body', '!=', ''), ('attachment_ids', '!=', False)]
                ])


                # Add author filter for ALL users (both authors and non-authors)
                if user.partner_id:
                    base_domain = expression.AND([
                        base_domain,
                        [('author_id', '=', user.partner_id.id)]
                    ])
                    if is_post_author:
                        print(f"Community Blog Filter Applied for Post Author: {user.name}")
                    else:
                        print(f"Community Blog Filter Applied for Non-Author User: {user.name}")

                # Check access
                Message = request.env['mail.message']
                if kw.get('token'):
                    access_as_sudo = _check_special_access(res_model, res_id, token=kw.get('token'))
                    if not access_as_sudo:
                        from werkzeug.exceptions import Forbidden
                        raise Forbidden()

                    if not request.env['res.users'].has_group('base.group_user'):
                        base_domain = expression.AND([Message._get_search_domain_share(), base_domain])
                    Message = request.env['mail.message'].sudo()

                # Fetch and return messages
                messages = Message.search(base_domain, limit=limit, offset=offset)
                message_count = Message.search_count(base_domain)

                formatted_msgs = messages.portal_message_format()

                return {
                    'messages': formatted_msgs,
                    'message_count': message_count
                }

        # For non-community blogs, use default behavior
        result = super(CommunityBlogPortalChatter, self).portal_message_fetch(
            res_model, res_id, domain=domain, limit=limit, offset=offset, **kw
        )
        return result