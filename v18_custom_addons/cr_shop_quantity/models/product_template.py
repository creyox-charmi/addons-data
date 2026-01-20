# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_sale_qty = fields.Integer('Min Sale Qty')
    max_sale_qty = fields.Integer('Max Sale Qty')
    qty_steps = fields.Integer('Quantity Steps')
