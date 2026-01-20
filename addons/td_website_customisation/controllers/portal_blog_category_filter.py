# -*- coding: utf-8 -*-

import werkzeug

from odoo import http
from odoo.http import request
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo import tools


class PortalBlogCategoryFilter(WebsiteBlog):

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
        is_not_all_blog_page = True

        if not blog:
            is_not_all_blog_page = False

        if not blog:
            return super(PortalBlogCategoryFilter, self).blog(blog=blog, tag=tag, page=page, search=search, **opt)

        # Parse categories and tags
        search_categories = self._parse_category_slugs(category)
        search_tags = self._parse_tag_slugs(tag)

        blog_post_env = request.env['blog.post'].sudo()

        # Build domain for filtering posts
        domain = [('blog_id', '=', blog.id), ('is_published', '=', True)]

        # Add search filter if present
        if search:
            domain += [
                '|', '|',
                ('name', 'ilike', search),
                ('subtitle', 'ilike', search),
                ('content', 'ilike', search)
            ]

        # Filter by tags with category ordering if tags are selected
        if search_tags:
            tag_param = tag if tag else ''
            tag_ids_ordered = [int(tid) for tid in tag_param.split(',') if tid.isdigit()]

            category_order = []
            seen_categories = set()

            for tag_id in tag_ids_ordered:
                tag_obj = request.env['blog.tag'].sudo().browse(tag_id)
                if tag_obj.exists() and tag_obj.category_id:
                    cat_id = tag_obj.category_id.id
                    if cat_id not in seen_categories:
                        category_order.append(cat_id)
                        seen_categories.add(cat_id)

            ordered_posts = request.env['blog.post'].sudo()
            seen_post_ids = set()

            for cat_id in category_order:
                category_tag_ids = [tid for tid in tag_ids_ordered
                                    if request.env['blog.tag'].sudo().browse(tid).category_id.id == cat_id]

                if category_tag_ids:
                    category_domain = domain + [('tag_ids', 'in', category_tag_ids)]
                    category_posts = blog_post_env.search(category_domain)

                    for post in category_posts:
                        if post.id not in seen_post_ids:
                            ordered_posts |= post
                            seen_post_ids.add(post.id)

            filtered_posts = ordered_posts
        else:
            cr_tags = []
            for data in blog.tag_category_ids:
                tags = request.env['blog.tag'].search([('category_id', '=', data.id)])
                for x in tags:
                    if x.id not in cr_tags:
                        cr_tags.append(x.id)

            if cr_tags:
                domain.append(('tag_ids', 'in', cr_tags))

            filtered_posts = blog_post_env.search(domain)

        # Prepare values using parent method but don't use its posts
        values = self._prepare_blog_values(
            blogs=blogs, blog=blog,
            date_begin=date_begin, date_end=date_end,
            tags=None,
            state=state, page=page, search=search
        )

        if isinstance(values, werkzeug.wrappers.Response):
            return values

        # Apply pagination manually
        post_per_page = self._blog_post_per_page if hasattr(self, '_blog_post_per_page') else 12
        total_posts = len(filtered_posts)

        offset = (page - 1) * post_per_page
        paginated_posts = filtered_posts[offset:offset + post_per_page]

        # Override posts and pager with our filtered and paginated results
        values['posts'] = paginated_posts
        values['pager'] = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=total_posts,
            page=page,
            step=post_per_page,
            url_args={'search': search, 'tag': tag, 'category': category},
        )
        values['search_count'] = total_posts

        if search_categories:
            available_tags = request.env['blog.tag'].sudo().search([
                ('category_id', 'in', search_categories.ids)
            ])
        else:
            available_tags = request.env['blog.tag']

        tag_categories = blog.tag_category_ids
        blog_url_base = '/blog/%s' % slug(blog)

        values.update({
            'blog_url': QueryURL(blog_url_base, ['tag', 'category'], blog=blog, tag=tag, category=category,
                                 date_begin=date_begin, date_end=date_end, search=search),
            'is_community_blog': is_community_blog,
            'is_not_all_blog_page': is_not_all_blog_page,
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

    def _prepare_blog_values(self, blogs, blog=False, date_begin=False, date_end=False, tags=False, state=False,
                             page=False, search=None):
        ref = super()._prepare_blog_values(blogs, blog, date_begin, date_end, tags, state, page, search)
        url_path = request.httprequest.path
        if url_path == '/blog':
            ref['display_cat'] = False
        else:
            ref['display_cat'] = True

        if tags:
            tag_ids = [int(tid) for tid in tags.split(',') if tid.isdigit()]
            ref['search_tags'] = request.env['blog.tag'].sudo().browse(tag_ids)
        else:
            ref['search_tags'] = request.env['blog.tag'].sudo()


        return ref
