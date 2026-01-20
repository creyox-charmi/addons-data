from odoo import fields, models, api
from datetime import date, datetime, timedelta
import pytz


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
    late_arrival_ids = fields.One2many('late.arrival.approval', 'employee_id', string='Late Arrival Counts')
    is_late_arrival_limit_crossed = fields.Boolean(default=False)
    exp_employee = fields.Boolean(default=False, string='Exceptional Employee')
      
    def is_checked_in_late(self):
        """checks if the user has checked in late or not"""

        def time_to_float(t):
            return t.hour + t.minute / 60 + t.second / 3600
        
        self.sudo().late_arrival_ids.compute_late_check_in_count()
        self.sudo().late_arrival_ids.compute_approval_btn_show()

        now = fields.Datetime.now()
        now_utc = pytz.utc.localize(now)
        tz = pytz.timezone(self.env.user.tz or "UTC")
        now_tz = now_utc.astimezone(tz)

        checked_out_entry = self.env["hr.attendance"].search(
            [("check_out", "=", False), ("employee_id", "=", self.id)]
        )
        if self.exp_employee:
            return False
        
        if checked_out_entry:
            return False
        else:
            if self.is_late_arrival_limit_crossed:
                return 'limit over'
            attendance_ids = self.resource_calendar_id.attendance_ids
            float_current_time = time_to_float(now_tz.time())
            todays_attendance_id = attendance_ids.filtered(
                lambda rec: int(rec.dayofweek) == now_tz.weekday()
                and float_current_time > rec.hour_from
                and float_current_time < rec.hour_to
            )
            if todays_attendance_id:
                if (
                    self.resource_calendar_id.check_in_delay_allowance
                    + todays_attendance_id.hour_from
                ) < float_current_time:
                    return True
                else:
                    return False
            else:
                return False
            
class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    is_late_arrival_limit_crossed = fields.Boolean(default=False)
    exp_employee = fields.Boolean(default=False, string='Exceptional Employee')