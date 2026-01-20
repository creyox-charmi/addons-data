import pytz
from odoo import models, fields, api, tools, _
from datetime import datetime

class HrAttendanceBreakAndResume(models.Model):
    _name = "hr.attendance.break.and.resume"
    _rec_name = 'formatted_time'

    attendance_id = fields.Many2one('hr.attendance',ondelete='cascade', store=True,copy=False,string='Attendance Reference')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    formatted_time = fields.Char(string="Formatted Time", compute='_get_formatted_time', store=True)
    attendance_break_state = fields.Selection(selection=[('break', 'Break'),('resume', 'Resume')],string="Break State", default='resume')
    break_time = fields.Datetime(string="Break Time")
    resume_time = fields.Datetime(string="Resume Time")
    break_hours = fields.Char(string='Break Hours', compute='_compute_total_break_hours', store=True, readonly=True)

    @api.depends('break_time', 'resume_time')
    def _get_formatted_time(self):
        for rec in self:
            break_time = False
            resume_time = False
            if rec.break_time:
                local_tz = pytz.timezone(self._context.get('tz') or 'UTC')
                break_time_tz = fields.Datetime.from_string(rec.break_time).replace(tzinfo=pytz.utc).astimezone(local_tz)
                break_time = (break_time_tz).time()
            if rec.resume_time:
                local_tz = pytz.timezone(self._context.get('tz') or 'UTC')
                resume_time_tz = fields.Datetime.from_string(rec.resume_time).replace(tzinfo=pytz.utc).astimezone(local_tz)
                resume_time = (resume_time_tz).time()
            break_time = str(break_time) if break_time else 'No Break Time'
            resume_time = str(resume_time) if resume_time else 'No Resume Time'
            rec.formatted_time  = f"{break_time} - {resume_time}"
    
    @api.depends('break_time', 'resume_time')
    def _compute_total_break_hours(self):
        dt_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
        for rec in self:
            if rec.break_time and rec.resume_time:
                break_time = datetime.strptime(str(rec.break_time), dt_format)
                resume_time = datetime.strptime(str(rec.resume_time), dt_format)
                delta = resume_time - break_time
                rec.break_hours = str(delta)