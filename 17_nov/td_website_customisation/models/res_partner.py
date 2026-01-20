# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_community_id(self):
        return self.env['blog.post'].sudo().blog_id.search([('name', 'ilike', 'comunidad')], limit=1)

    def get_unread_messages_by_user(self):
        current_partner = self.env.user.partner_id
        blog_blog = self._get_community_id()

        my_blog_post = self.env['blog.post'].sudo().search([
            ('blog_id', '=', blog_blog.id),
            ('author_id', '=', current_partner.id)
        ], limit=1)

        other_blog_posts = self.env['blog.post'].sudo().search([
            ('blog_id', '=', blog_blog.id),
            ('author_id', '!=', current_partner.id)
        ])

        user_unread = {}

        # Messages in current user's blog
        if my_blog_post:
            for msg in my_blog_post.message_ids.filtered(
                    lambda m: m.message_type == 'comment' and
                              m.author_id != current_partner and
                              not m.is_read_by_partner(current_partner.id)
            ):
                author_id = msg.author_id.id
                if author_id not in user_unread:
                    user_unread[author_id] = {'partner': msg.author_id, 'count': 0}
                user_unread[author_id]['count'] += 1

        # Messages in others' blogs where current user is a partner
        for post in other_blog_posts:
            for msg in post.message_ids.filtered(
                    lambda m: m.message_type == 'comment' and
                              m.author_id != current_partner and
                              m.partner_ids and
                              current_partner in m.partner_ids and
                              not m.is_read_by_partner(current_partner.id)
            ):
                author_id = post.author_id.id
                if author_id not in user_unread:
                    user_unread[author_id] = {'partner': post.author_id, 'count': 0}
                user_unread[author_id]['count'] += 1

        return [{'partner': data['partner'], 'unread_count': data['count']}
                for data in user_unread.values()]

    def get_total_unread_count(self):
        return sum(item['unread_count'] for item in self.get_unread_messages_by_user())


