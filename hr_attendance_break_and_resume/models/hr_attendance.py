import pytz
from odoo import models, fields, api, tools, _
from datetime import datetime

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    break_ids = fields.One2many('hr.attendance.break.and.resume', 'attendance_id', help='List the attendance breaks for the employee.', string="Break")
    break_hours = fields.Char(string='Break Hours', compute='_compute_total_break_hours', store=True, readonly=True)
    net_hours = fields.Char(string='Net Hours', compute='_compute_net_hours', store=True, readonly=True)

    @api.depends('break_ids.break_time', 'break_ids.resume_time')
    def _compute_total_break_hours(self):
        for record in self:
            total_seconds = 0
            for break_record in record.break_ids:
                if break_record.break_time and break_record.resume_time:
                    # Calculate the break duration in seconds
                    break_duration = (break_record.resume_time - break_record.break_time).total_seconds()
                    total_seconds += break_duration
            
            # Convert total seconds to hours and minutes, discarding seconds
            hours, remaining_seconds = divmod(int(total_seconds), 3600)
            minutes = remaining_seconds // 60
            record.break_hours = "%02d:%02d" % (hours, minutes)

    @api.depends('worked_hours', 'break_hours')
    def _compute_net_hours(self):
        for record in self:
            # Convert worked_hours to seconds
            worked_seconds = int(float(record.worked_hours) * 3600) if record.worked_hours else 0
            
            # Convert break_hours (formatted as HH:MM) to seconds
            break_seconds = 0
            if record.break_hours:
                hours, minutes = map(int, record.break_hours.split(':'))
                break_seconds = (hours * 3600) + (minutes * 60)

            # Calculate net_seconds by subtracting break_seconds from worked_seconds
            net_seconds = max(0, worked_seconds - break_seconds)
            
            # Convert net_seconds back to hours and minutes, discarding seconds
            hours, remaining_seconds = divmod(net_seconds, 3600)
            minutes = remaining_seconds // 60
            record.net_hours = "%02d:%02d" % (hours, minutes)