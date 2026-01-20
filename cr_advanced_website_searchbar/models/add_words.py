# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models, _


class AddWords(models.Model):
    _name = "cr.add.words"
    _description = "Add Words"

    name = fields.Char("Name")
