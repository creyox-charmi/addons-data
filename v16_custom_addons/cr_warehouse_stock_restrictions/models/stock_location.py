# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = "stock.location"

    user_id = fields.Many2many(string="user_id", comodel_name="res.users")
