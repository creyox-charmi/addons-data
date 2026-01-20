# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields

class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    is_show_in_parts_picker = fields.Boolean(
        string="Is Show In Parts Picker",
        default=True
    )
    allow_multiple_products = fields.Boolean(
        string="Allow Multiple Products",
        help="If checked, users can add multiple products under this category in the parts picker."
    )
