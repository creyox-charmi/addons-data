# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _

class StockLot(models.Model):
    _inherit = "stock.lot"

    quantity  = fields.Boolean(string='Quantity',default=False)

    @api.depends('quant_ids', 'quant_ids.quantity')
    def _product_qty(self):
        res = super(StockLot, self)._product_qty()
        for lot in self:
            quants = lot.quant_ids.filtered(lambda q: q.location_id.usage == 'internal' or (
                    q.location_id.usage == 'transit' and q.location_id.company_id))
            if not quants:
                if len(lot.quant_ids) == 1:
                    if lot.quantity == False:
                        lot.product_qty = lot.quant_ids.quantity
                        lot.quantity = True
        return res