# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom', 'product_id')
    def _compute_price_unit(self):
        for line in self:
            if line.order_id.pricelist_id:
                pricelist_item = line.order_id.pricelist_id.item_ids
                if pricelist_item:
                    price = line.order_id.pricelist_id.item_ids.search(
                        [('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                         ('pricelist_id', '=', line.order_id.pricelist_id.id),
                         ('uom_id', '=', line.product_uom.id)])
                    if price:
                        line.price_unit = price.fixed_price
                    else:
                        uom_ratio = line.product_uom._compute_quantity(1, line.product_id.uom_id)
                        line.price_unit = line.product_id.list_price * uom_ratio
                else:
                    uom_ratio = line.product_uom._compute_quantity(1, line.product_id.uom_id)
                    line.price_unit = line.product_id.list_price * uom_ratio
            else:
                super(SaleOrderLine, line)._compute_price_unit()