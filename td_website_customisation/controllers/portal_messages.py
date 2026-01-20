# -*- coding: utf-8 -*-

from odoo.addons.wb_portal_blogs.controllers.controllers import CustomerPortalBlogsController
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, exceptions
from odoo.http import request
from odoo.addons.wb_portal_blogs.controllers.controllers import CustomerPortalBlogsController
from odoo.addons.wb_portal_blogs.controllers.portal import CustomerPortalBlogs as portal
import logging

_logger = logging.getLogger(__name__)


class PortalMessagesExtended(CustomerPortalBlogsController):


    @http.route(['/my/messages', '/my/messages/page/<int:page>'], auth='user', website=True)
    def myMessagesListView(self, page=1, **kw):
        current_partner = request.env.user.partner_id
        blog_blog_id = self._get_community_id()

        my_blog_post = request.env['blog.post'].sudo().search([
            ('blog_id', '=', blog_blog_id.id),
            ('author_id', '=', current_partner.id)
        ], limit=1)

        other_blog_posts = request.env['blog.post'].sudo().search([
            ('blog_id', '=', blog_blog_id.id),
            ('author_id', '!=', current_partner.id)
        ])

        commenters = {}

        # Messages in current user's blog
        if my_blog_post:
            for msg in my_blog_post.message_ids.filtered(lambda m: m.message_type == 'comment'):
                if msg.author_id != current_partner:
                    # Messages from others
                    if msg.author_id.id not in commenters:
                        commenters[msg.author_id.id] = {
                            'partner': msg.author_id,
                            'message_count': 0,
                            'unread_count': 0
                        }
                    commenters[msg.author_id.id]['message_count'] += 1
                    if not msg.is_read_by_partner(current_partner.id):
                        commenters[msg.author_id.id]['unread_count'] += 1

                elif msg.author_id == current_partner and msg.partner_ids:
                    # Messages sent by current user to others
                    for partner in msg.partner_ids:
                        if partner.id not in commenters:
                            commenters[partner.id] = {
                                'partner': partner,
                                'message_count': 0,
                                'unread_count': 0
                            }
                        commenters[partner.id]['message_count'] += 1


        for post in other_blog_posts:
            for msg in post.message_ids.filtered(
                    lambda m: m.message_type == 'comment' and m.author_id == current_partner):
                author = post.author_id
                if author.id not in commenters:
                    commenters[author.id] = {
                        'partner': author,
                        'message_count': 0,
                        'unread_count': 0
                    }
                commenters[author.id]['message_count'] += 1

            for msg in post.message_ids.filtered(
                    lambda m: m.message_type == 'comment' and m.author_id != current_partner
                            and m.partner_ids and current_partner in m.partner_ids):
                author = post.author_id
                if author.id not in commenters:
                    commenters[author.id] = {
                        'partner': author,
                        'message_count': 0,
                        'unread_count': 0
                    }
                commenters[author.id]['message_count'] += 1
                if not msg.is_read_by_partner(current_partner.id):
                    commenters[msg.author_id.id]['unread_count'] += 1

        message_list = [{
            'partner': data['partner'],
            'message_count': data['message_count'],
            'unread_count': data['unread_count']
        } for data in commenters.values()]

        message_list.sort(key=lambda x: (x['unread_count'], x['message_count']), reverse=True)

        pager = request.website.pager(
            url='/my/messages',
            total=len(message_list),
            page=page,
            step=self._items_per_page,
            scope=7
        )

        return request.render("td_website_customisation.portal_my_messages_list_view_extended", {
            'message_ids': message_list[pager['offset']:pager['offset'] + self._items_per_page],
            'pager': pager,
            'page_name': 'my_messages',
            'breadcrumb': [('/my/home', 'Inicio'), ('/my/messages', 'Mis Mensajes')],
        })

    @http.route(['/my/messages/thread/<int:partner_id>'], type='http', auth="user", website=True, csrf=True)
    def portal_messages_thread(self, partner_id, **kwargs):
        current_partner_id = request.env.user.partner_id.id
        other_partner = request.env['res.partner'].sudo().browse(partner_id)
        blog_blog_id = self._get_community_id()

        my_blog_post = request.env['blog.post'].sudo().search([
            ('blog_id', '=', blog_blog_id.id),
            ('author_id', '=', current_partner_id)
        ], limit=1)

        other_blog_post = request.env['blog.post'].sudo().search([
            ('blog_id', '=', blog_blog_id.id),
            ('author_id', '=', partner_id)
        ], limit=1)

        all_messages = request.env['mail.message']

        if my_blog_post:
            my_blog_messages = my_blog_post.message_ids.filtered(
                lambda m: (
                        m.message_type == 'comment' and (
                        (
                                m.author_id.id == current_partner_id and m.partner_ids and other_partner.id in m.partner_ids.ids)
                        or
                        (m.author_id.id == other_partner.id)
                )
                )
            )
            all_messages |= my_blog_messages

        if other_blog_post:
            other_blog_messages = other_blog_post.message_ids.filtered(
                lambda m: m.message_type == 'comment' and
                          m.author_id.id == current_partner_id
            )
            all_messages |= other_blog_messages

        if other_blog_post:
            other_blog_messages = other_blog_post.message_ids.filtered(
                lambda m: m.message_type == 'comment' and
                          m.author_id.id == other_partner.id
                and m.partner_ids and current_partner_id in m.partner_ids.ids
            )
            all_messages |= other_blog_messages

        is_portal_msg_of_partner = request.env['mail.message'].search(
            [('is_portal_reply', '=', True), ('author_id', '=', other_partner.id)])
        if is_portal_msg_of_partner:
            portal_msg_of_partner= is_portal_msg_of_partner.filtered(
                lambda m: (
                        m.message_type == 'comment' and (
                    (
                            m.partner_ids and current_partner_id in m.partner_ids.ids)
                )
                )
            )
            all_messages |= portal_msg_of_partner

        all_messages = all_messages.sorted('create_date')


        for msg in all_messages:
            if msg.author_id.id != current_partner_id:
                msg.sudo().mark_as_read_by_partner(current_partner_id)
            if msg.parent_id:
                msg.parent_id = msg.parent_id.exists()

        return request.render("td_website_customisation.portal_my_messages_thread_view", {
            'messages': all_messages,
            'other_partner': other_partner,
            'current_partner': request.env.user.partner_id,
            'my_blog_post': my_blog_post,
            'other_blog_post': other_blog_post,
            'page_name': 'my_messages',
            'breadcrumb': [
                ('/my/home', 'Inicio'),
                ('/my/messages', 'Mis Mensajes'),
                ('#', other_partner.name)
            ],
        })

    @http.route(['/my/messages/send'], type='json', auth="user", methods=['POST'])
    def post_message_send(self, body, parent_message_id=False, blog_post_id=False, other_partner_id=False,
                          parent_body=False, **kwargs):
        try:
            current_partner_id = request.env.user.partner_id.id
            blog_post = request.env['blog.post'].sudo().browse(int(blog_post_id))

            if not blog_post:
                return {'error': 'No se encontró el blog post'}

            message_vals = {
                'body': body,
                'message_type': 'comment',
                'subtype_xmlid': 'mail.mt_comment',
                'author_id': current_partner_id,
                'partner_ids': [int(other_partner_id)],
                'is_portal_reply': bool(parent_message_id),
            }

            if parent_message_id:
                message_vals['parent_id'] = int(parent_message_id)
                if parent_body:
                    message_vals['portal_reply_body'] = parent_body

            new_message = blog_post.with_context(mail_create_nosubscribe=True).sudo().message_post(**message_vals)

            if parent_message_id and parent_body:
                new_message.sudo().write({'portal_reply_body': parent_body})

            return {
                'success': True,
                'message_id': new_message.id
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route(['/my/messages/unread'], type='json', auth="user")
    def get_unread_messages(self, **kwargs):
        """Get unread messages grouped by user for bell notification"""
        current_partner = request.env.user.partner_id
        blog_blog_id = self._get_community_id()

        my_blog_post = request.env['blog.post'].sudo().search([
            ('blog_id', '=', blog_blog_id.id),
            ('author_id', '=', current_partner.id)
        ], limit=1)

        unread_by_user = {}

        if my_blog_post:
            for msg in my_blog_post.message_ids.filtered(
                    lambda m: m.message_type == 'comment' and m.author_id != current_partner):
                if not msg.is_read_by_partner(current_partner.id):
                    if msg.author_id.id not in unread_by_user:
                        unread_by_user[msg.author_id.id] = {
                            'partner_id': msg.author_id.id,
                            'partner_name': msg.author_id.name,
                            'partner_image': f'/web/image/res.partner/{msg.author_id.id}/image_128',
                            'unread_count': 0
                        }
                    unread_by_user[msg.author_id.id]['unread_count'] += 1

        return {
            'unread_users': list(unread_by_user.values()),
            'total_unread': sum(u['unread_count'] for u in unread_by_user.values())
        }

    @http.route(['/my/messages/mark_read/<int:partner_id>'], type='json', auth="user")
    def mark_conversation_read(self, partner_id, **kwargs):
        """Mark all messages from a specific user as read"""
        current_partner_id = request.env.user.partner_id.id
        blog_blog_id = self._get_community_id()

        my_blog_post = request.env['blog.post'].sudo().search([
            ('blog_id', '=', blog_blog_id.id),
            ('author_id', '=', current_partner_id)
        ], limit=1)

        if my_blog_post:
            messages_to_mark = my_blog_post.message_ids.filtered(
                lambda m: m.message_type == 'comment' and
                          m.author_id.id == partner_id and
                          not m.is_read_by_partner(current_partner_id)
            )
            for msg in messages_to_mark:
                msg.sudo().mark_as_read_by_partner(current_partner_id)

        return {'success': True}


    @http.route('/my/blog/edit/<int:blog_id>', type='http', auth="user", website=True, csrf=True,
                methods=['GET', 'POST'])
    def portal_blog_edit_profile(self, blog_id, **kwargs):
        """Override to add category data to context"""
        BlogPost = request.env['blog.post'].sudo()
        blog_blog_id = self._get_community_id()
        blog_entry = BlogPost.browse(blog_id)
        partner = request.env.user.partner_id
        blog_posts = blog_entry or BlogPost.search(portal._get_blogs_domain(self, partner.id)).filtered(
            lambda x: x.blog_id.id == blog_blog_id.id
        )

        if not blog_posts:
            vals = {
                'blog_id': blog_blog_id.id,
                'name': kwargs.get('name') or request.env.user.partner_id.name,
                'subtitle': '',
                'content': '',
                'is_published': False,
            }
            blog_entry = BlogPost.create(vals)
            blog_id = blog_entry.id

        if blog_entry.create_uid.partner_id != request.env.user.partner_id:
            return request.redirect('/my/blogs')

        if request.httprequest.method == 'POST':
            try:
                tag_ids = [int(value) for key, value in kwargs.items() if key.startswith("category-")]

                available_category_ids = []
                if 'available_category_ids' in request.httprequest.form:
                    avail_cats = request.httprequest.form.getlist('available_category_ids')
                    available_category_ids = [(6, 0, [int(cat_id) for cat_id in avail_cats])]

                import base64
                import re

                multimedia_updates = []
                multimedia_indices = sorted(
                    list(set(re.findall(r"multimedia_ids\[(-?\d+)]\.id", ' '.join(kwargs.keys())))), key=int)

                for multimedia_index in multimedia_indices:
                    multimedia_id = int(kwargs.get('multimedia_ids[%s].id' % multimedia_index))
                    multimedia_type = kwargs.get('multimedia_ids[%s].content_type' % multimedia_index)
                    multimedia_url = kwargs.get('multimedia_ids[%s].content_url' % multimedia_index)

                    multimedia_file = request.httprequest.files.get(
                        'multimedia_ids[%s].content_file' % multimedia_index)

                    file_data = False
                    filename = kwargs.get('multimedia_ids[%s].content_file_filename' % multimedia_index)
                    mimetype = kwargs.get('multimedia_ids[%s].content_file_mimetype' % multimedia_index)

                    if multimedia_file and multimedia_file.filename:
                        file_data = base64.b64encode(multimedia_file.read())
                        filename = multimedia_file.filename
                        mimetype = multimedia_file.content_type

                    multimedia_vals = {
                        'content_type': multimedia_type,
                        'content_url': multimedia_url,
                    }
                    if file_data:
                        multimedia_vals['content_file'] = file_data
                        multimedia_vals['content_file_filename'] = filename
                        multimedia_vals['content_file_mimetype'] = mimetype

                    if multimedia_id > 0:
                        multimedia_updates.append((1, multimedia_id, multimedia_vals))
                    elif file_data or multimedia_url:
                        multimedia_updates.append((0, 0, multimedia_vals))

                current_multimedia_ids = blog_entry.multimedia_ids.ids
                submitted_multimedia_ids = [m[1] for m in multimedia_updates if m[0] == 1]
                multimedia_to_remove = list(set(current_multimedia_ids) - set(submitted_multimedia_ids))
                for multimedia_id in multimedia_to_remove:
                    multimedia_updates.append((2, multimedia_id))

                vals = {
                    'name': kwargs.get('name'),
                    'subtitle': kwargs.get('subtitle'),
                    'is_published': kwargs.get('is_published') == '1',
                    'only_text_content': kwargs.get('only_text_content'),
                    'website_meta_title': kwargs.get('website_meta_title'),
                    'website_meta_description': kwargs.get('website_meta_description'),
                    'website_meta_keywords': kwargs.get('website_meta_keywords'),
                    'tag_ids': [(6, 0, tag_ids)],
                    'available_category_ids': available_category_ids,  # ADD THIS LINE
                    'cover_properties': self._get_background_json(
                        kwargs.get('bg-img') or f'/web/image/blog.post/{blog_entry.id}/blog_entry_html'),
                    'multimedia_ids': multimedia_updates,
                }

                blog_entry_html_file = request.httprequest.files.get('blog_entry_html')
                if blog_entry_html_file and blog_entry_html_file.filename:
                    vals['blog_entry_html'] = base64.b64encode(blog_entry_html_file.read())

                main_image_file = request.httprequest.files.get('main_image')
                if main_image_file and main_image_file.filename:
                    vals['main_image'] = base64.b64encode(main_image_file.read())

                social_media_fields = [
                    'facebook_url',
                    'instagram_url',
                    'linkedin_url',
                    'twitter_url',
                    'youtube_url',
                    'github_url'
                ]

                author_vals = {}
                for field in social_media_fields:
                    url = kwargs.get(field, False)
                    author_vals[field] = url

                if author_vals:
                    blog_entry.author_id.write(author_vals)

                blog_entry.sudo().write(vals)

                multimedia_html = request.env['ir.ui.view']._render_template(
                    "wb_portal_blogs.portal_blog_multimedia_html",
                    {
                        'dynamic_text_content': blog_entry.only_text_content or '',
                        'id': blog_entry.id,
                        'multimedia_items': blog_entry.multimedia_ids,
                    }
                )

                vals = {
                    'content': multimedia_html,
                }

                blog_entry.sudo().write(vals)

                return request.redirect('/my/blog/edit/%s?success=1' % blog_id)
            except exceptions.UserError as e:
                _logger.exception(e)
                return request.redirect('/my/blog/edit/%s?error=1' % blog_id)
            except Exception as e:
                _logger.exception(e)
                return request.redirect('/my/blog/edit/%s?error=1' % blog_id)

        multimedia_items = blog_entry.multimedia_ids or request.env['blog.post.multimedia'].sudo()

        multimedia_html = request.env['ir.ui.view']._render_template(
            "wb_portal_blogs.portal_blog_multimedia_html",
            {
                'dynamic_text_content': blog_entry.only_text_content or '',
                'id': blog_entry.id,
                'multimedia_items': multimedia_items,
            }
        )

        full_content = multimedia_html

        CrBlog = request.env['blog.blog'].sudo().search([('name', 'ilike', 'comunidad')], limit=1)
        tag_categories = CrBlog.tag_category_ids

        # tag_categories = request.env['blog.tag.category'].sudo().search([])

        selected_categories = blog_entry.tag_ids.mapped('category_id') if blog_entry.tag_ids else []

        values = {
            'action': 'edit' if blog_id > 0 else 'new',
            'page_name': 'blog_edit',
            'blog_entry': blog_entry,
            'blog_entry_html': self._extract_image_html(blog_entry.cover_properties),
            'blog_ids': blog_blog_id,
            'tag_ids': request.env['blog.tag'].sudo().search([]),
            'tag_categories': tag_categories,
            'selected_categories': selected_categories,
            'full_content': full_content,
        }

        if kwargs.get('success'):
            values['error'] = False
        if kwargs.get('error'):
            values['error'] = True

        return request.render("wb_portal_blogs.portal_my_blogs_form_view_edit", values)

class CustomerPortalBlogsInherit(CustomerPortal):

    def _get_community_id(self):
        BlogPost = request.env['blog.post'].sudo()
        return BlogPost.blog_id.search([('name', 'ilike', 'comunidad')], limit=1)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        current_partner = request.env.user.partner_id
        blog_blog_id = self._get_community_id()

        if 'message_count' in counters:  # ONLY check for message_count
            my_blog_post = request.env['blog.post'].sudo().search([
                ('blog_id', '=', blog_blog_id.id),
                ('author_id', '=', current_partner.id)
            ], limit=1)

            other_blog_posts = request.env['blog.post'].sudo().search([
                ('blog_id', '=', blog_blog_id.id),
                ('author_id', '!=', current_partner.id)
            ])

            total_msg_count = 0
            total_unread_count = 0

            if my_blog_post:
                for msg in my_blog_post.message_ids.filtered(lambda m: m.message_type == 'comment'):
                    if msg.author_id != current_partner:
                        total_msg_count += 1
                        try:
                            if not msg.is_read_by_partner(current_partner.id):
                                total_unread_count += 1
                        except Exception:
                            pass
                    elif msg.author_id == current_partner and msg.partner_ids:
                        total_msg_count += len(msg.partner_ids)

            for post in other_blog_posts:
                for msg in post.message_ids.filtered(
                        lambda m: m.message_type == 'comment' and m.author_id == current_partner):
                    total_msg_count += 1

                for msg in post.message_ids.filtered(
                        lambda m: m.message_type == 'comment'
                                  and m.author_id != current_partner
                                  and m.partner_ids
                                  and current_partner in m.partner_ids
                ):
                    total_msg_count += 1
                    try:
                        if not msg.is_read_by_partner(current_partner.id):
                            total_unread_count += 1
                    except Exception:
                        pass

            values['message_count'] = total_msg_count

        return values


class BlogPostInherit(http.Controller):
    """Mark messages as read when viewing blog post"""

    @http.route(['/blog/<model("blog.blog"):blog>/post/<model("blog.post"):blog_post>'],
                type='http', auth="public", website=True)
    def blog_post(self, blog, blog_post, **kwargs):
        """Override to mark messages as read when viewing blog post"""
        if request.env.user and request.env.user.partner_id:
            current_partner_id = request.env.user.partner_id.id

            # Mark all comments in this post as read by current user
            comments = blog_post.message_ids.filtered(
                lambda m: m.message_type == 'comment' and m.author_id.id != current_partner_id
            )
            for comment in comments:
                comment.sudo().mark_as_read_by_partner(current_partner_id)

        # Call original method (you may need to adjust this based on original controller)
        return request.render("website_blog.blog_post_complete", {
            'blog': blog,
            'blog_post': blog_post,
            'main_object': blog_post,
        })

