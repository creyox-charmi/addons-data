# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import json
from odoo import http
from odoo.http import request
import random

class BlogController(http.Controller):

    @http.route('/blog/random', auth="public", type="http", methods=['GET'])
    def random_blog_posts(self):
        """
        Method to retrieve random 4 blog posts from the 'blog.post' model
        """
        blog_posts = request.env['blog.post'].search([])

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
