# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api

class HrAttendanceBreakReason(models.Model):
    _name = 'hr.attendance.break.reason'
    _description = 'Attendance Break Reason'
    _order = 'name'

    name = fields.Char(string='Reason', required=True, translate=True,store=True)
    active = fields.Boolean(default=True,store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_company_unique', 'unique(name, company_id)', 'Reason must be unique per company!')
    ]