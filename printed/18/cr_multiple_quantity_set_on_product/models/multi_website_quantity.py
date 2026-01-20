# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import fields, models

class MultiWebsiteQuantity(models.Model):
    _name = 'multi.website.quantity'
    _description = 'Set Product Quantity on Multiple Website'

    website_id = fields.Many2one('website', string='Website')
    quantity = fields.Integer('Quantity', default=1)
    product_id = fields.Many2one('product.template', readonly=True)
