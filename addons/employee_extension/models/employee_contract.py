from odoo import api, models, fields, _


class EmployeeContractInherit(models.Model):
    _inherit = 'hr.contract'
    free_field_13 = fields.Char(string='Free Field 13')
    free_field_14 = fields.Char(string='Free Field 14')
    free_field_15 = fields.Char(string='Free Field 15')
    free_field_16 = fields.Char(string='Free Field 16')
    gross_full_salary = fields.Integer(string='Gross full time Salary')
    part_time_percent = fields.Integer(string='Part time Percentage')
    scale = fields.Integer(string='Scale')
    step = fields.Integer(string='Step')
    employee_no_wage = fields.Integer(string='Employee Number Wages')
    duration_contract_in_month = fields.Integer(string='Duration Contract In Month')
    employment_no = fields.Char(string='Employment Number')
    periodic = fields.Integer(string='Periodic')
    date_service = fields.Date("Date Service")
    probation_end = fields.Date("Probation Ends")
    wage = fields.Monetary('Wage', tracking=True, help="Employee's monthly gross wage.")