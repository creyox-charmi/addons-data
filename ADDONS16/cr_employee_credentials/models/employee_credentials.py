from odoo import fields, models, api

class EmployeeCredentials(models.Model):
    _name = 'cr.employee.credentials'

    name = fields.Many2one('cr.login.platform', string = "Login Platform")
    login = fields.Char(string = "Login ID")
    password = fields.Char(string = "Password")
    other = fields.Char(string = "Other")
    employee_id = fields.Many2one('hr.employee')
