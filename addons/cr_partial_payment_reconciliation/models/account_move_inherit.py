# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_to_pay = fields.Float(string="Amount to Pay")
