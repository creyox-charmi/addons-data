# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    overhead_data_ids = fields.One2many(
        comodel_name="cr.overhead.data", inverse_name="cr_mrp_id", string="Overhead"
    )
