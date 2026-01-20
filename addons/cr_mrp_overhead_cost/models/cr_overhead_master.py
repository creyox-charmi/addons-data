# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models, _


class OverheadMaster(models.Model):
    _name = "cr.overhead.master"

    code = fields.Integer(string="Code")
    name = fields.Char(string="name")
    description = fields.Char(string="Description")
    debit_account_id = fields.Many2one(
        comodel_name="account.account", string="Debit Account"
    )
    credit_account_id = fields.Many2one(
        comodel_name="account.account", string="Credit Account"
    )
