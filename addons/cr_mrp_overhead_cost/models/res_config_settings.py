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

    cr_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        related="company_id.cr_journal_id",
        store=True,
        readonly=False,
    )
