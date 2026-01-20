from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    split = fields.Boolean(string='Split')
