# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('name', 'default_code')
    def _compute_display_name(self):
        for template in self:
            # Show only product name, ignore default_code
            template.display_name = template.name or ''
