# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import api, fields, models, _


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    cr_cash_register_name = fields.Char(string='Cash Register')


