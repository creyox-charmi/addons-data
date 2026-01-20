# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import fields, models


class Categories(models.Model):
    _name = "cr.categories"
    _description = "App Categories"

    name = fields.Char(string="Name")
