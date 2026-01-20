# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    is_show_in_parts_picker = fields.Boolean(
        string="Want To Show In Parts Picker ?", default=True
    )
    allow_multiple_products = fields.Boolean(
        string="Want To Allow Multiple Products ?",
        help="If checked, users can add multiple products under this category in the parts picker.",
    )
    is_optional = fields.Boolean(string="Optional Category ?")
