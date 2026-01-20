# -*- coding: utf-8 -*-
# Part of Creyox technologies.
from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
