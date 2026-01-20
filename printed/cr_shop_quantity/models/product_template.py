# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_sale_qty = fields.Integer('Min Sale Qty')
    max_sale_qty = fields.Integer('Max Sale Qty')
    qty_steps = fields.Integer('Quantity Steps')

    def get_pricelist_info(self):
        """
        This method fetches the pricelist details for the current product template.
        It can return multiple pricelists if applicable.
        """
        # Fetch the pricelist records related to this product template
        print(self.id)
        print('self.product_variant_id : ',self.product_variant_id)
        pricelist_records = self.env['product.pricelist.item'].search([
            ('product_tmpl_id', '=', self.id)
        ])

        return pricelist_records

    def get_product_quantity_details(self):
        print("call")
        return {
            'min_sale_qty': self.min_sale_qty or 1,
            'max_sale_qty': self.max_sale_qty or 1000,
            'qty_steps': self.qty_steps or 1,
        }