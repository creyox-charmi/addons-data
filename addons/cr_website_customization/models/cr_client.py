# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import base64

from odoo import api, fields, models, _

class Client(models.Model):
    _name = "cr.client"
    _description = "Client"

    name = fields.Char(string="Client Name")
    logo = fields.Binary(string="Logo")
    active = fields.Boolean(string="active")
