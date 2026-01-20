# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import json
import random
import re

from odoo import http
from odoo.http import request
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.http_routing.models.ir_http import slug, unslug

class CrWebsiteBlog(WebsiteBlog):

    @http.route([
        '/blog',
        '/blog/page/<int:page>',
        '/blog/tag/<string:tag>',
        '/blog/tag/<string:tag>/page/<int:page>',
        '''/blog_post/all''',
        '''/blog/<model("blog.tag"):tags>''',
        '''/blog/<model("blog.blog"):blog>''',
        '''/blog/<model("blog.blog"):blog>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
        '/blog/featured',
        '/blog/featured/page/<int:page>',  # Paginated featured blogs
    ], type='http', auth="public", website=True, sitemap=True)
    def blog(self, blog=None, tag=None, page=1, search=None, **opt):
        response = super(CrWebsiteBlog, self).blog(blog, tag, page, search, **opt)
        return response


    def _prepare_blog_values(self, blogs, blog=False, date_begin=False, date_end=False, tags=False, state=False, page=False, search=None):
        ref = super(CrWebsiteBlog,self)._prepare_blog_values(blogs, blog, date_begin, date_end, tags, state, page, search)
        url_path = request.httprequest.path

        # Regular expression to capture the slug and id (slug-id pattern)
        match = re.search(r'/blog/([^/]+)-(\d+)', url_path)

        if match:
            slug_name = match.group(1)  # Extract the slug
            blog_id = match.group(2)  # Extract the ID
            tag_list = request.env['blog.tag'].search([
                ('id','=',blog_id),
                ('name', '=', slug_name)
            ])
            ref['tag_list'] = tag_list
            ref['no_of_record_display'] = len(tag_list.post_ids)
            ref['is_latest_post'] = False
        elif url_path == '/blog_post/all':
            ref['tag_list'] = None
            ref['no_of_record_display'] = len(ref['posts'])
            ref['is_latest_post'] = True
        else:
            tag_list = request.env['blog.tag'].search([])
            ref['tag_list'] = tag_list
            ref['no_of_record_display'] = 6
            ref['is_latest_post'] = True


        return ref

    @http.route(['/cr/blog/tag/<model("blog.tag"):tag>'], type='http', auth="public", website=True)
    def blog_tag_page(self, tag, **kw):
        # Fetch all blog posts associated with the selected tag
        blog_tag = request.env['blog.tag'].search([('id', '=', tag.id)])

        return request.redirect("/blog/%s" % (slug(blog_tag)))

    @http.route(['/cr/blog/tag/Latest'], type='http', auth="public", website=True)
    def blog_tag_page_all(self, **kw):
        return request.redirect("/blog_post/all")

    @http.route('/blog/random', auth="public", type="http", methods=['GET'])
    def random_blog_posts(self,**kwargs):
        """
        Method to retrieve random 4 blog posts from the 'blog.post' model
        """
        blog_id = kwargs.get('id')
        print("blog_id : ",blog_id)
        url_path = request.httprequest.path
        print("url_path : ",url_path)
        blog_posts = request.env['blog.post'].search([('id','!=',blog_id)])
        print("blog_posts : ",blog_posts)

        if blog_posts:
            random_blog_posts = random.sample(blog_posts, min(4, len(blog_posts)))

            blog_data = []
            for blog in random_blog_posts:
                blog_data.append({
                    'title': blog.name,
                    'subtitle': blog.subtitle,
                    'background_color': blog.background_color,
                    'author_name': blog.author_name,
                    'content': blog.content,
                    'url': blog.website_url,
                    'teaser': blog.teaser or blog.teaser_manual
                })
            return request.make_response(json.dumps(blog_data), headers={'Content-Type': 'application/json'})

        else:
            return {'error': 'No blog posts found'}





