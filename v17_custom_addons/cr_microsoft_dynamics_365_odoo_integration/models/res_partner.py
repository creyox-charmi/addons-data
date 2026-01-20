# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    source = fields.Char('Source', help="Origin of the partner record")
    x_dynamics_id = fields.Char('Dynamics ID', index=True)
    x_revenue = fields.Float('Revenue')
    x_employee_count = fields.Integer('Employee Count')
    x_dynamics_account_id = fields.Char('Dynamics Account ID', index=True)