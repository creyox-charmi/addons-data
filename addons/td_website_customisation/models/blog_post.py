# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class BlogPost(models.Model):
    _inherit = 'blog.post'

    def _compute_tag_categories(self):
        for post in self:
            categories = post.tag_ids.mapped('category_id')
            post.tag_category_ids = categories

    def _td_get_all_available_tags(self):
        AvailableCategories = self.blog_id and self.blog_id.tag_category_ids and self.blog_id.tag_category_ids
        if AvailableCategories:
            return AvailableCategories.mapped('tag_ids').ids
        return self.env['blog.tag'].search([]).ids

    @api.depends('blog_id', 'blog_id.tag_category_ids')
    def _compute_available_tag_ids(self):
        for rec in self:
            rec.td_available_tags_ids = [Command.clear()] + [Command.set(rec._td_get_all_available_tags())]

    tag_category_ids = fields.Many2many(
        comodel_name='blog.tag.category',
        compute='_compute_tag_categories',
        string='Tag Categories',
        store=False
    )
    td_available_tags_ids = fields.Many2many(
        comodel_name='blog.tag',
        relation="td_available_category_tag_domain",
        compute='_compute_available_tag_ids',
        string='Available Tags Domains',
        store=True
    )

