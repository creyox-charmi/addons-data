# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    td_order_type = fields.Selection(
        selection=[
            ("kronos", "Kronos"),
            ("kronos_lab", "Kronos Lab"),
        ],
        string="Order Type",
        default="kronos",
    )
