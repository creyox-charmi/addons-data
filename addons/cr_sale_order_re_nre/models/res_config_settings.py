# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    restrict_sale_order_line_remove = fields.Boolean(
        "Allow Sale Order Line Remove",
        config_parameter="sale.order.line.remove",
        help="Allow removing confirmed sale order lines only "
        "if they are not invoiced or delivered.",
    )