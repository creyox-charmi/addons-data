# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    cr_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Stock journal",
        domain="[('type', 'in',( 'bank','cash'))]"
    )
    cr_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Stock Account Valuation",
        domain="[('account_type', '=', 'asset_current'),('reconcile','=',True)]"
    )
    cr_is_activate_account = fields.Boolean(
        string='Activate accounts when transfer between different storage locations',
        related="company_id.cr_is_activate_account",
        readonly=False,
        store=True)
