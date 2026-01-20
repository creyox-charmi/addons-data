# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, api, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    catalog_qty = fields.Float(
        string='Catalog Quantity',
        compute='_compute_catalog_qty',
        store=False
    )

    @api.depends_context('order_id')
    def _compute_catalog_qty(self):
        order_id = self.env.context.get('order_id')
        if not order_id:
            self.catalog_qty = 0.0
            return

        order = self.env['sale.order'].browse(order_id)
        for product in self:
            line = order.order_line.filtered(
                lambda l: l.product_id == product and not l.display_type
            )
            product.catalog_qty = sum(line.mapped('product_uom_qty'))