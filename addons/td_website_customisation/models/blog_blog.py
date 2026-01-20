# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BlogBlog(models.Model):
    _inherit = 'blog.blog'

    tag_category_ids = fields.Many2many(
        'blog.tag.category',
        string='Tag Categories',
    )

