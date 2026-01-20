# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    show_catalog_tree_view = fields.Boolean(
        string='Show Catalog as Tree View',
        default=False,
        help='If enabled, product catalog will open in tree view instead of kanban view'
    )