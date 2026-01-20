# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import fields, api, models


class Version(models.Model):
    _name = "cr.versions.odoo"
    _description = "Odoo Version"

    name = fields.Char(string="Name")
