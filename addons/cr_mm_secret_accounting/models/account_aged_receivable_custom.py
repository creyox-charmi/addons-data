# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import api, models, _, fields


class AgedReceivableCustom(models.AbstractModel):
    _name = "account.aged.receivable.custom"
    _description = "Aged Receivable (Custom)"
    _inherit = "account.aged.receivable.report.handler"
