# -*- coding: utf-8 -*-

from odoo import models, fields

class BlogPost(models.Model):
    _inherit = 'blog.post'

    def _compute_tag_categories(self):
        for post in self:
            categories = post.tag_ids.mapped('category_id')
            post.tag_category_ids = categories

    tag_category_ids = fields.Many2many(
        'blog.tag.category',
        compute='_compute_tag_categories',
        string='Tag Categories',
        store=False
    )
    available_category_ids = fields.Many2many('blog.available.category', string='Available Categories')

