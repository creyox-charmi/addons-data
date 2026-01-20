# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models

class PerProductShipping(models.Model):
    _name = 'cr.per.product.shipping'
    _description = 'Per Product Shipping'

    product_template_id = fields.Many2one(comodel_name='product.template',
                                          string='Product')
    delivery_carrier_id = fields.Many2one(comodel_name='delivery.carrier',
                                          string='Delivery Method')

    delivery_carrier_ids = fields.Many2many(comodel_name='delivery.carrier',string='Allowed Delivery Methods')

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        """Method for assign Available Delivery Methods"""
        if self.product_template_id:
            self.delivery_carrier_ids = self.product_template_id.cr_delivery_carrier_ids

