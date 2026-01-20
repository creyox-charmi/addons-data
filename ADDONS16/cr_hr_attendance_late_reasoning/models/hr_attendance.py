from odoo import models, fields, api
from datetime import datetime
import pytz


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    late_reason = fields.Char(string="Late Reasoning")

    def late_reason_assigning(self, rzn):
        """writes the late reason in database"""

        obj = self.sudo().write({"late_reason": rzn})
        rec=self.env['late.arrival.approval'].sudo().search([('employee_id', '=', self.employee_id.id),('month', '=', str(datetime.now().month)),('year','=', str(datetime.now().year))])

        if not rec:
            rec = self.env['late.arrival.approval'].sudo().create({
                'employee_id': self.employee_id.id,
                'month': str(datetime.now().month),
                'year' : str(datetime.now().year),
                'approval_btn_show' : True 
            })
        return obj

    def write(self, vals):
        """if user checks in late then it notifies the admins that the employee has checked in at that time."""
        rec = super().write(vals)
        group_system = self.env.ref("base.group_system")

        users_with_admin_settings = self.env["res.users"].search(
            [("groups_id", "in", group_system.id)]
        )

        if vals.get("late_reason") != None:
            current_time_hm = datetime.now(pytz.timezone("Asia/Kolkata")).strftime(
                "%H:%M"
            )

            for user in users_with_admin_settings:
                message = {
                    "title": f"{self.employee_id.name} checked in at {current_time_hm}",
                    "type": "warning",
                    "message": f"reason: {self.late_reason}",
                    "sticky": True,
                }
                self.env["bus.bus"]._sendone(
                    user.partner_id, "simple_notification", message
                )
        else:
            pass
        return rec

