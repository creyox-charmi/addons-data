# -*- coding: utf-8 -*-

from odoo import models, fields


class BlogAvailableCategory(models.Model):
    _name = 'blog.available.category'
    _description = 'Blog Available Category'

    name = fields.Char(string='Name', required=True)
