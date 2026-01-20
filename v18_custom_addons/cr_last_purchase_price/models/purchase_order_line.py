from collections import defaultdict
from odoo import models,fields, api,_
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from xlwt.ExcelMagic import ptgInt


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_override_price = fields.Boolean(string="Override Price")
    product_cost = fields.Float(string="Current Unit Cost", readonly=True)

    @api.onchange('is_override_price')
    def _onchange_override_price(self):
        if self.is_override_price:
            self.product_cost = self.product_id.standard_price  # Set product_cost to the product's current standard price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_cost = self.product_id.standard_price

    @api.model
    def create(self, vals):
        print("create")
        if not self.is_override_price:
            if self.product_id:
                self.product_cost = self.product_id.standard_price
        return super(PurchaseOrderLine, self).create(vals)


