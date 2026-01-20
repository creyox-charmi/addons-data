# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _

class StockQuant(models.Model):
    _inherit = "stock.quant"

    temp_quantity  = fields.Boolean(string='Quantity',default=False)