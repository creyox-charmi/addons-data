# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import api, models, _, fields
from odoo import models, fields, api, _, osv

class PartnerLedgerCustom(models.AbstractModel):
    _name = "account.partner.ledger.custom"
    _description = "Partner Ledger (Custom)"
    _inherit = "account.partner.ledger.report.handler"


