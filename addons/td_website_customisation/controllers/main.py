# -*- coding: utf-8 -*-

import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class TDWebsiteCustomisation(http.Controller):
    _items_per_page = 10

    @http.route('/my/messages/mark_read', type='http', auth="user", methods=['POST'], csrf=True)
    def mark_messages_read(self, **kwargs):
        """Mark messages as read for a specific blog post and partner"""
        try:
            blog_id = kwargs.get('blog_id')
            partner_id = kwargs.get('partner_id')

            if not blog_id or not partner_id:
                return request.make_json_response({'error': 'Missing parameters'}, status=400)

            blog_id = int(blog_id)
            partner_id = int(partner_id)

            blog_post = request.env['blog.post'].browse(blog_id)
            if not blog_post.exists() or blog_post.author_id.id != request.env.user.partner_id.id:
                return request.make_json_response({'error': 'Unauthorized'}, status=403)

            messages = request.env['mail.message'].search([
                ('model', '=', 'blog.post'),
                ('res_id', '=', blog_id),
                ('message_type', '=', 'comment'),
                ('author_id', '=', partner_id),
                ('is_read_by_blog_author', '=', False)
            ])

            if messages:
                messages.write({'is_read_by_blog_author': True})

            return request.make_json_response({
                'success': True,
                'marked_count': len(messages)
            })

        except Exception as e:
            return request.make_json_response({'error': str(e)}, status=500)

    @http.route('/my/messages/unread_count', type='json', auth="user", methods=['POST'])
    def get_unread_count(self, **kwargs):
        """Get current unread message count for AJAX updates"""
        try:
            count = request.env.user.partner_id.get_unread_blog_messages_count()
            unread_by_blog = request.env.user.partner_id.get_unread_messages_by_blog()

            return {
                'total_count': count,
                'by_blog': [{
                    'blog_id': item['blog_post'].id,
                    'blog_name': item['blog_post'].name,
                    'unread_count': item['unread_count'],
                    'latest_author': item['latest_message'].author_id.name if item['latest_message'] else '',
                } for item in unread_by_blog]
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/my/messages/mark_all_read', type='json', auth="user", methods=['POST'])
    def mark_all_messages_read(self, **kwargs):
        """Mark all unread messages as read for current user's blog posts"""
        try:
            current_user = request.env.user
            blog_posts = request.env['blog.post'].search([
                ('author_id', '=', current_user.partner_id.id)
            ])

            messages = request.env['mail.message'].search([
                ('model', '=', 'blog.post'),
                ('res_id', 'in', blog_posts.ids),
                ('message_type', '=', 'comment'),
                ('author_id', '!=', current_user.partner_id.id),
                ('is_read_by_blog_author', '=', False)
            ])

            if messages:
                messages.write({'is_read_by_blog_author': True})

            return {
                'success': True,
                'marked_count': len(messages)
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route(['/my/messages/thread/partner/<int:partner_id>/blog/<int:blog_id>'], type='http', auth="user",
                website=True, csrf=True)
    def portal_messages_profile(self, partner_id, blog_id, **kwargs):
        values = {}
        try:
            blog_entry = partner = None

            if blog_id and partner_id:
                blog_entry = request.env['blog.post'].sudo().browse(blog_id)
                partner = request.env['res.partner'].sudo().browse(partner_id)

                # Mark messages as read automatically for current user
                try:
                    unread_messages = request.env['mail.message'].sudo().search([
                        ('model', '=', 'blog.post'),
                        ('res_id', '=', blog_id),
                        ('message_type', '!=', 'user_notification'),
                        ('author_id', '=', partner_id),
                        ('read_by_partner_ids', '!=', request.env.user.partner_id.id),  # <-- changed
                    ])
                    if unread_messages:
                        for msg in unread_messages:
                            msg.sudo().write({
                                'read_by_partner_ids': [(4, request.env.user.partner_id.id)]
                            })
                except Exception as e:
                    _logger.error("Error marking messages read: %s", e)

            # Get all blog posts for the partner
            blog_posts = request.env['blog.post'].sudo().search([('author_id', '=', partner_id)])
            unread_counts = {}
            for post in blog_posts:
                unread_counts[post.id] = request.env['mail.message'].sudo().search_count([
                    ('model', '=', 'blog.post'),
                    ('res_id', '=', post.id),
                    ('message_type', '!=', 'user_notification'),
                    ('author_id', '!=', request.env.user.partner_id.id),
                    ('read_by_partner_ids', '!=', request.env.user.partner_id.id),  # <-- changed
                ])

            values = {
                'blog_entry': blog_entry,
                'partner': partner,
                'blog_posts': blog_posts,
                'unread_counts': unread_counts,
            }

        except Exception as exc:
            _logger.error("Error in portal_messages_profile: %s", exc)
            values.update({'error': True})

        return request.render("wb_portal_blogs.portal_my_messages_form_view", values)

    @http.route(['/my/messages', '/my/messages/page/<int:page>'], auth='user', website=True)
    def myMessagesListView(self, page=1, **kw):
        current_partner = request.env.user.partner_id
        blog_blog_id = self._get_community_id()

        # Get blog posts with messages
        blog_posts_messages = request.env['blog.post'].sudo().search([]).filtered(
            lambda x: x.blog_id.id == blog_blog_id.id and x.message_ids
        )

        message_ids = []
        for bpm in blog_posts_messages:
            author_ids = bpm.message_ids.filtered(lambda x: x.author_id.id != current_partner.id).author_id
            for a in author_ids:
                # All messages by this author on this blog post
                message_set = bpm.message_ids.filtered(lambda x: x.author_id.id == a.id)

                # 🔥 Compute unread count for this user (instead of in template)
                unread_count = request.env['mail.message'].sudo().search_count([
                    ('model', '=', 'blog.post'),
                    ('res_id', '=', bpm.id),
                    ('message_type', '=', 'comment'),
                    ('author_id', '!=', current_partner.id),
                    ('id', 'not in', request.env['mail.message'].sudo().search([
                        ('res_id', '=', bpm.id),
                        ('model', '=', 'blog.post'),
                        ('read_by_partner_ids', 'in', current_partner.id)
                    ]).ids)
                ])

                message_ids.append({
                    'blog_id': bpm,
                    'message_id': message_set,
                    'count_message': len(message_set),
                    'unread_count': unread_count,  # ✅ pass to template
                })

        pager = request.website.pager(
            url='/my/messages',
            total=len(message_ids),
            page=page,
            step=self._items_per_page,
            scope=7
        )

        return request.render("wb_portal_blogs.portal_my_messages_list_view", {
            'message_ids': message_ids[pager['offset']:pager['offset'] + self._items_per_page],
            'pager': pager,
            'page_name': 'my_messages',
            'breadcrumb': [('/my/home', 'Inicio'), ('/my/messages', 'Mis Mensajes')],
        })

    def _get_community_id(self):
        BlogPost = request.env['blog.post'].sudo()
        return BlogPost.blog_id.search([('name', 'ilike', 'comunidad')], limit=1)
