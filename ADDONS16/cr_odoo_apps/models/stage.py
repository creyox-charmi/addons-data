# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import fields, models, api


class Stage(models.Model):
    _name = "cr.stage"
    _description = "Stage"

    name = fields.Char(string="Name")
    is_done = fields.Boolean(string="Is done stage?", default=False, store=True)
    is_draft = fields.Boolean(string="Is draft stage?", default=False, store=True)
    color = fields.Integer(string="Color")
    active = fields.Boolean(default=True)
