from odoo import models,fields, api,_

class StockMove(models.Model):
    _inherit = "stock.move"

    updated_price = fields.Float(string="Updated Price")
    product_cost = fields.Float( string="Cost Price")

    @api.model
    def create(self, vals):
        if 'purchase_line_id' in vals:
            purchase_line = self.env['purchase.order.line'].browse(vals['purchase_line_id'])
            if purchase_line.is_override_price:
                vals['product_cost'] = purchase_line.product_cost

        return super(StockMove, self).create(vals)
