# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cr_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        domain="[('type', '=', 'general')]",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cr_company_id = fields.Many2one("res.company", string="Company")
    cr_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        related="cr_company_id.cr_journal_id",
        readonly=False,
    )
