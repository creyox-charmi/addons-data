from odoo import fields, models, api
from datetime import timedelta


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    leave_days = fields.Integer(string="Leave Days", compute="compute_leave_days")

    def compute_leave_days(self):
        """counts leave days for public holiday"""
        for record in self:
            if record.date_to and record.date_from:
                workdays = {
                    int(workday.dayofweek)
                    for workday in record.calendar_id.attendance_ids
                }
                delta = record.date_to - record.date_from
                leave_days = (
                    sum(
                        1
                        for i in range(delta.days)
                        if (record.date_from + timedelta(days=i)).weekday() in workdays
                    )
                    + 1
                )
                record.leave_days = leave_days
            else:
                record.leave_days = 0
