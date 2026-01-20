# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _

class StockLot(models.Model):
    _inherit = "stock.lot"

    quantity  = fields.Boolean(string='Quantity',default=False)

