# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _


class Purchase(models.Model):
    _inherit = "purchase.order"

    workorder_id = fields.Many2one("mrp.workorder", string="Work Order")
    mrp_id = fields.Many2one("mrp.production", string="Manufacturing")
