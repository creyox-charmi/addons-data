# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    cr_overhead_data_ids = fields.One2many(
        comodel_name="cr.overhead.data", inverse_name="mrp_id", string="Overhead"
    )
