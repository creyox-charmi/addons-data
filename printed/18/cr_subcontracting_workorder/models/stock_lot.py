# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api, _

class StockLot(models.Model):
    _inherit = "stock.lot"

    quantity  = fields.Boolean(string='Quantity',default=False)

    # @api.depends('quant_ids', 'quant_ids.quantity')
    # def _product_qty(self):
    #     res = super(StockLot, self)._product_qty()  # Call base method
    #     print("afterrrrrr....................")
    #     for lot in self:
    #         print(f"Computing product_qty for Lot: {lot.name}")
    #         print("Original product_qty:", lot.product_qty)
    #         print('lot.env.context.get("picking_type") : ',lot.env.context.get("picking_type"))
    #         for lot in self:
    #             # We only care for the quants in internal or transit locations.
    #             quants = lot.quant_ids.filtered(lambda q: q.location_id.usage == 'internal' or (
    #                         q.location_id.usage == 'transit' and q.location_id.company_id))
    #             if quants:
    #                 print("if")
    #                 print("Applying custom logic for outgoing stock")
    #                 print("Before")
    #                 print('lot.product_qty : ',lot.product_qty)
    #                 print("self.quantity : ",self.quantity)
    #                 lot.product_qty = self.quantity + 1
    #                 self.quantity = lot.product_qty
    #                 print("After")
    #                 print('lot.product_qty : ', lot.product_qty)
    #                 print("self.quantity : ", self.quantity)
    #             else:
    #                 if len(lot.quant_ids) == 1:
    #
    #                 print("else")
    #                 print("Applying custom logic for outgoing stock")
    #                 print("Before")
    #                 print('lot.product_qty : ', lot.product_qty)
    #                 print("self.quantity : ", self.quantity)
    #                 lot.product_qty = lot.product_qty - 1
    #                 self.quantity = lot.product_qty
    #                 print("After")
    #                 print('lot.product_qty : ', lot.product_qty)
    #                 print("self.quantity : ", self.quantity)
    #
    #         print("Updated product_qty:", lot.product_qty)
    #
    #     return res

    @api.depends('quant_ids', 'quant_ids.quantity')
    def _product_qty(self):
        res = super(StockLot, self)._product_qty()  # Call base method
        print("afterrrrrr....................")
        for lot in self:
            for lot in self:
                # We only care for the quants in internal or transit locations.
                quants = lot.quant_ids.filtered(lambda q: q.location_id.usage == 'internal' or (
                        q.location_id.usage == 'transit' and q.location_id.company_id))
                if not quants:
                    if len(lot.quant_ids) == 1:
                        if lot.quantity == False:
                            print("YESSS BASEEE")
                            lot.product_qty = lot.quant_ids.quantity
                            lot.quantity = True
        return res