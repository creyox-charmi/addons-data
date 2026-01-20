# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import http
from odoo.http import request
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
import werkzeug
from odoo import tools


class PortalBlogCategoryFilter(WebsiteBlog):

    # Update these functions in controller:

    def _slugify_categories(self, category_ids, toggle_category_id=None):
        """Prepares comma separated category IDs for URLs"""
        category_ids = list(category_ids) if category_ids else []

        if toggle_category_id:
            if toggle_category_id in category_ids:
                category_ids.remove(toggle_category_id)
            else:
                category_ids.append(toggle_category_id)

        if not category_ids:
            return ''

        return ','.join(str(cid) for cid in category_ids)

    def _slugify_tags(self, tag_ids, toggle_tag_id=None):
        """Prepares comma separated tag IDs for URLs"""
        tag_ids = list(tag_ids) if tag_ids else []

        if toggle_tag_id:
            if toggle_tag_id in tag_ids:
                tag_ids.remove(toggle_tag_id)
            else:
                tag_ids.append(toggle_tag_id)

        if not tag_ids:
            return ''

        return ','.join(str(tid) for tid in tag_ids)

    def _parse_category_slugs(self, slug_categories):
        """Parse comma-separated category IDs"""
        CategoryModel = request.env['blog.tag.category']
        if not slug_categories:
            return CategoryModel

        try:
            category_ids = [int(cid) for cid in slug_categories.split(',') if cid.isdigit()]
            return CategoryModel.sudo().browse(category_ids) if category_ids else CategoryModel
        except:
            return CategoryModel

    def _parse_tag_slugs(self, slug_tags):
        """Parse comma-separated tag IDs"""
        BlogTag = request.env['blog.tag']
        if not slug_tags:
            return BlogTag

        try:
            tag_ids = [int(tid) for tid in slug_tags.split(',') if tid.isdigit()]
            return BlogTag.sudo().browse(tag_ids) if tag_ids else BlogTag
        except:
            return BlogTag


    def _slugify_tags_for_categories(self, tag_ids, category_ids, toggle_category_id):
        """Remove tags when their category is unselected"""
        if toggle_category_id not in category_ids:
            return self._slugify_tags(tag_ids)

        # Category being removed - remove its tags
        category = request.env['blog.tag.category'].sudo().browse(toggle_category_id)
        category_tag_ids = category.tag_ids.ids

        remaining_tag_ids = [tid for tid in tag_ids if tid not in category_tag_ids]
        return self._slugify_tags(remaining_tag_ids)



    # Updated controller - Add category route

    # @http.route([
    #     '/blog',
    #     '/blog/page/<int:page>',
    #     '/blog/tag/<string:tag>',
    #     '/blog/tag/<string:tag>/page/<int:page>',
    #     '/blog/category/<string:category>',
    #     '/blog/category/<string:category>/page/<int:page>',
    #     '/blog/category/<string:category>/tag/<string:tag>',
    #     '/blog/category/<string:category>/tag/<string:tag>/page/<int:page>',
    #     '''/blog/<model("blog.blog"):blog>''',
    #     '''/blog/<model("blog.blog"):blog>/page/<int:page>''',
    #     '''/blog/<model("blog.blog"):blog>/tag/<string:tag>''',
    #     '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
    #     '''/blog/<model("blog.blog"):blog>/category/<string:category>''',
    #     '''/blog/<model("blog.blog"):blog>/category/<string:category>/page/<int:page>''',
    #     '''/blog/<model("blog.blog"):blog>/category/<string:category>/tag/<string:tag>''',
    #     '''/blog/<model("blog.blog"):blog>/category/<string:category>/tag/<string:tag>/page/<int:page>''',
    #     '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/category/<string:category>''',
    #     '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/category/<string:category>/page/<int:page>''',
    # ], type='http', auth="public", website=True, sitemap=True)
    # def blog(self, blog=None, tag=None, page=1, search=None, category=None, **opt):
    #     Blog = request.env['blog.blog']
    #     blogs = tools.lazy(lambda: Blog.search(request.website.website_domain(), order="create_date asc, id asc"))
    #
    #     if not blog and len(blogs) == 1:
    #         url = QueryURL('/blog/%s' % slug(blogs[0]), search=search, **opt)()
    #         return request.redirect(url, code=302)
    #
    #     date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')
    #
    #     community_blog = request.env['blog.blog'].sudo().search([('name', 'ilike', 'comunidad')], limit=1)
    #     is_community_blog = blog and community_blog and blog.id == community_blog.id
    #
    #     if not is_community_blog:
    #         return super(PortalBlogCategoryFilter, self).blog(blog=blog, tag=tag, page=page, search=search, **opt)
    #
    #     values = self._prepare_blog_values(blogs=blogs, blog=blog, date_begin=date_begin, date_end=date_end, tags=tag, state=state, page=page, search=search)
    #
    #     if isinstance(values, werkzeug.wrappers.Response):
    #         return values
    #
    #     if blog:
    #         values['main_object'] = blog
    #
    #     search_categories = self._parse_category_slugs(category)
    #     search_tags = self._parse_tag_slugs(tag)
    #
    #
    #     # --- Handle category and tag filters ---
    #     blog_post_env = request.env['blog.post'].sudo()
    #
    #     domain = [('blog_id', '=', blog.id)]  # base domain for blog
    #
    #     # If categories are selected, filter posts that have at least one tag belonging to those categories
    #     if search_categories:
    #         domain.append(('tag_ids.category_id', 'in', search_categories.ids))
    #
    #     # If tags are selected, filter posts by those tags as well
    #     if search_tags:
    #         domain.append(('tag_ids', 'in', search_tags.ids))
    #
    #
    #     search_categories = self._parse_category_slugs(category)
    #     search_tags = self._parse_tag_slugs(tag)
    #
    #     blog_post_env = request.env['blog.post'].sudo()
    #
    #     if search_tags:
    #         # Track the order in which categories appear in the tag parameter
    #         tag_param = tag if tag else ''
    #         tag_ids_ordered = [int(tid) for tid in tag_param.split(',') if tid.isdigit()]
    #
    #         # Get category order based on tag selection order
    #         category_order = []
    #         seen_categories = set()
    #
    #         for tag_id in tag_ids_ordered:
    #             tag_obj = request.env['blog.tag'].sudo().browse(tag_id)
    #             if tag_obj.exists() and tag_obj.category_id:
    #                 cat_id = tag_obj.category_id.id
    #                 if cat_id not in seen_categories:
    #                     category_order.append(cat_id)
    #                     seen_categories.add(cat_id)
    #
    #
    #         # Fetch posts ordered by category selection
    #         ordered_posts = request.env['blog.post'].sudo()
    #         seen_post_ids = set()
    #
    #         for cat_id in category_order:
    #             # Get tags from this category that are selected
    #             category_tag_ids = [tid for tid in tag_ids_ordered
    #                                 if request.env['blog.tag'].sudo().browse(tid).category_id.id == cat_id]
    #
    #             if category_tag_ids:
    #                 category_domain = [
    #                     ('blog_id', '=', blog.id),
    #                     ('tag_ids', 'in', category_tag_ids)
    #                 ]
    #
    #                 category_posts = blog_post_env.search(category_domain)
    #
    #                 for post in category_posts:
    #                     if post.id not in seen_post_ids:
    #                         ordered_posts |= post
    #                         seen_post_ids.add(post.id)
    #
    #         filtered_posts = ordered_posts
    #     else:
    #         # No tags selected, show all posts from blog
    #         filtered_posts = blog_post_env.search([('blog_id', '=', blog.id)])
    #
    #     # Call _prepare_blog_values with original tag parameter
    #     values = self._prepare_blog_values(
    #         blogs=blogs, blog=blog,
    #         date_begin=date_begin, date_end=date_end,
    #         tags=tag,
    #         state=state, page=page, search=search
    #     )
    #
    #     if isinstance(values, werkzeug.wrappers.Response):
    #         return values
    #
    #     # Override posts with filtered results
    #     values['posts'] = filtered_posts
    #
    #     # --- Build available tags and categories for UI ---
    #     if search_categories:
    #         available_tags = request.env['blog.tag'].sudo().search([
    #             ('category_id', 'in', search_categories.ids)
    #         ])
    #     else:
    #         available_tags = request.env['blog.tag']
    #
    #     tag_categories = request.env['blog.tag.category'].sudo().search([])
    #
    #     blog_url_base = '/blog/%s' % slug(blog)
    #
    #     values.update({
    #         'blog_url': QueryURL(blog_url_base, ['tag', 'category'], blog=blog, tag=tag, category=category,
    #                              date_begin=date_begin, date_end=date_end, search=search),
    #         'is_community_blog': True,
    #         'tag_categories': tag_categories,
    #         'search_categories': search_categories,
    #         'search_tags': search_tags,
    #         'available_tags': available_tags,
    #         'slugify_categories': self._slugify_categories,
    #         'slugify_tags': self._slugify_tags,
    #         'slugify_tags_for_categories': self._slugify_tags_for_categories,
    #         'blog_query_url': lambda **kw: QueryURL(blog_url_base, ['tag', 'category'], **kw),
    #     })
    #
    #     return request.render("website_blog.blog_post_short", values)

    @http.route([
        '/blog',
        '/blog/page/<int:page>',
        '/blog/tag/<string:tag>',
        '/blog/tag/<string:tag>/page/<int:page>',
        '/blog/category/<string:category>',
        '/blog/category/<string:category>/page/<int:page>',
        '/blog/category/<string:category>/tag/<string:tag>',
        '/blog/category/<string:category>/tag/<string:tag>/page/<int:page>',
        '''/blog/<model("blog.blog"):blog>''',
        '''/blog/<model("blog.blog"):blog>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/category/<string:category>''',
        '''/blog/<model("blog.blog"):blog>/category/<string:category>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/category/<string:category>/tag/<string:tag>''',
        '''/blog/<model("blog.blog"):blog>/category/<string:category>/tag/<string:tag>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/category/<string:category>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/category/<string:category>/page/<int:page>''',
    ], type='http', auth="public", website=True, sitemap=True)
    def blog(self, blog=None, tag=None, page=1, search=None, category=None, **opt):
        Blog = request.env['blog.blog']
        blogs = tools.lazy(lambda: Blog.search(request.website.website_domain(), order="create_date asc, id asc"))

        if not blog and len(blogs) == 1:
            url = QueryURL('/blog/%s' % slug(blogs[0]), search=search, **opt)()
            return request.redirect(url, code=302)

        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')

        community_blog = request.env['blog.blog'].sudo().search([('name', 'ilike', 'comunidad')], limit=1)
        is_community_blog = blog and community_blog and blog.id == community_blog.id

        if not is_community_blog:
            return super(PortalBlogCategoryFilter, self).blog(blog=blog, tag=tag, page=page, search=search, **opt)

        values = self._prepare_blog_values(blogs=blogs, blog=blog, date_begin=date_begin, date_end=date_end, tags=tag,
                                           state=state, page=page, search=search)

        if isinstance(values, werkzeug.wrappers.Response):
            return values

        if blog:
            values['main_object'] = blog

        search_categories = self._parse_category_slugs(category)
        search_tags = self._parse_tag_slugs(tag)

        # --- Handle category and tag filters ---
        blog_post_env = request.env['blog.post'].sudo()

        domain = [('blog_id', '=', blog.id)]  # base domain for blog

        # If categories are selected, filter posts that have at least one tag belonging to those categories
        if search_categories:
            domain.append(('tag_ids.category_id', 'in', search_categories.ids))

        # If tags are selected, filter posts by those tags as well
        if search_tags:
            domain.append(('tag_ids', 'in', search_tags.ids))

        search_categories = self._parse_category_slugs(category)
        search_tags = self._parse_tag_slugs(tag)

        blog_post_env = request.env['blog.post'].sudo()

        if search_tags:
            # Track the order in which categories appear in the tag parameter
            tag_param = tag if tag else ''
            tag_ids_ordered = [int(tid) for tid in tag_param.split(',') if tid.isdigit()]

            # Get category order based on tag selection order
            category_order = []
            seen_categories = set()

            for tag_id in tag_ids_ordered:
                tag_obj = request.env['blog.tag'].sudo().browse(tag_id)
                if tag_obj.exists() and tag_obj.category_id:
                    cat_id = tag_obj.category_id.id
                    if cat_id not in seen_categories:
                        category_order.append(cat_id)
                        seen_categories.add(cat_id)

            # Fetch posts ordered by category selection
            ordered_posts = request.env['blog.post'].sudo()
            seen_post_ids = set()

            for cat_id in category_order:
                # Get tags from this category that are selected
                category_tag_ids = [tid for tid in tag_ids_ordered
                                    if request.env['blog.tag'].sudo().browse(tid).category_id.id == cat_id]

                if category_tag_ids:
                    category_domain = [
                        ('blog_id', '=', blog.id),
                        ('tag_ids', 'in', category_tag_ids)
                    ]

                    category_posts = blog_post_env.search(category_domain)

                    for post in category_posts:
                        if post.id not in seen_post_ids:
                            ordered_posts |= post
                            seen_post_ids.add(post.id)

            filtered_posts = ordered_posts
        else:
            # No tags selected, show all posts from blog
            filtered_posts = blog_post_env.search([('blog_id', '=', blog.id)])

        # Call _prepare_blog_values with original tag parameter
        values = self._prepare_blog_values(
            blogs=blogs, blog=blog,
            date_begin=date_begin, date_end=date_end,
            tags=tag,
            state=state, page=page, search=search
        )

        if isinstance(values, werkzeug.wrappers.Response):
            return values

        # Override posts with filtered results
        values['posts'] = filtered_posts

        # --- Build available tags and categories for UI ---
        if search_categories:
            available_tags = request.env['blog.tag'].sudo().search([
                ('category_id', 'in', search_categories.ids)
            ])
        else:
            available_tags = request.env['blog.tag']

        tag_categories = request.env['blog.tag.category'].sudo().search([])

        blog_url_base = '/blog/%s' % slug(blog)

        values.update({
            'blog_url': QueryURL(blog_url_base, ['tag', 'category'], blog=blog, tag=tag, category=category,
                                 date_begin=date_begin, date_end=date_end, search=search),
            'is_community_blog': True,
            'tag_categories': tag_categories,
            'search_categories': search_categories,
            'search_tags': search_tags,
            'available_tags': available_tags,
            'slugify_categories': self._slugify_categories,
            'slugify_tags': self._slugify_tags,
            'slugify_tags_for_categories': self._slugify_tags_for_categories,
            'blog_query_url': lambda **kw: QueryURL(blog_url_base, ['tag', 'category'], **kw),
        })

        return request.render("website_blog.blog_post_short", values)
