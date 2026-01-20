# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class Color(models.Model):
    _name = 'color.management'
    _description = 'Color Management'

    name = fields.Char(string='Color Name', required=True)
    color_code = fields.Char(string='Color Code', required=True)