# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import api, models, _, fields


class AgedPayableCustom(models.Model):
    _name = "account.aged.payable.custom"
    _description = "Aged Payable (Custom)"
    _inherit = "account.aged.payable.report.handler"
