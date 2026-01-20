# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    part_number = fields.Char(string='Part Number')