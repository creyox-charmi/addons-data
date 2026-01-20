# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cr_is_activate_account = fields.Boolean(
        string='Activate accounts when transfer between different storage locations')
    cr_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Inter-Locations Clearing Account",
        check_company=True,
        domain="[('account_type', '=', 'asset_current'),('reconcile','=',True)]"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cr_is_activate_account = fields.Boolean(
        string='Activate accounts when transfer between different storage locations',
        related="company_id.cr_is_activate_account",
        readonly=False,
        store=True)
    cr_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Inter-Locations Clearing Account",
        domain="[('account_type', '=', 'asset_current'),('reconcile','=',True)]",
        related="company_id.cr_account_id",
        check_company=True,
        readonly=False,
        store=True
    )
