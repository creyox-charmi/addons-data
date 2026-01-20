# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models, _


class OverheadData(models.Model):
    _name = "cr.production.data"

    overhead_master_id = fields.Many2one(
        comodel_name="cr.overhead.master", string="Overhead"
    )
    cost = fields.Integer(string="Cost Per Unit")
    subtotal = fields.Integer(string="Subtotal")
    mrp_production_id = fields.Many2one("mrp.production")
