from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    hr_attendance_break_and_resume = fields.Boolean(string="Enable Attendance Break", default=False)
    hr_attendance_break_and_resume_k = fields.Boolean(string="Enable Attendance Break", readonly=False)