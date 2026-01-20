# -*- coding: utf-8 -*-
from odoo import models

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def write(self, vals):
        res = super().write(vals)
        if 'quantity' in vals or 'location_id' in vals:
            # Trigger recompute for affected products
            affected_products = self.mapped('product_id')
            bom_lines = self.env['mrp.bom.line'].search([
                ('product_id', 'in', affected_products.ids)
            ])
            if bom_lines:
                bom_lines._compute_free_to_use()
        return res

    def create(self, vals_list):
        res = super().create(vals_list)
        affected_products = res.mapped('product_id')
        bom_lines = self.env['mrp.bom.line'].search([
            ('product_id', 'in', affected_products.ids)
        ])
        if bom_lines:
            bom_lines._compute_free_to_use()
        return res