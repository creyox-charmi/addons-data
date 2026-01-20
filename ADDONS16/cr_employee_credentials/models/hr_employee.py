from odoo import fields, models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_credentials_line = fields.One2many('cr.employee.credentials','employee_id')