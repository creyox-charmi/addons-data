# -*- coding: utf-8 -*-
from odoo import models, fields


class StateValue(models.Model):
    _name = 'state.value'
    _description = 'State Value'

    name = fields.Char()
    key = fields.Char()
    field_id = fields.Many2one('ir.model.fields')

