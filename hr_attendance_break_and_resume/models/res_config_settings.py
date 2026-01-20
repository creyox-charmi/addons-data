from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    hr_attendance_break_and_resume = fields.Boolean(related="company_id.hr_attendance_break_and_resume", string="Enable Attendance Break", readonly=False, 
        config_parameter='hr_attendance_break_and_resume')
    hr_attendance_break_and_resume_k = fields.Boolean(related="company_id.hr_attendance_break_and_resume_k", string="Enable Attendance Break", readonly=False,
        config_parameter='hr_attendance_break_and_resume_k')