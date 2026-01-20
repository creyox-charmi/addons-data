# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import api, models, _, fields


class PartnerLedgerCustom(models.AbstractModel):
    _name = "account.partner.ledger.custom"
    _description = "Partner Ledger (Custom)"
    _inherit = "account.partner.ledger.report.handler"
