# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields


class BlogTagCategory(models.Model):
    _inherit = 'blog.tag.category'

    color = fields.Char(string='Color', default='#17a2b8')