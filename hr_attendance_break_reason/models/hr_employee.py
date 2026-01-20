# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, api
from odoo.fields import Datetime

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def attendance_break_resume_action(self, reason_id=None):
        self.ensure_one()
        action_date = Datetime.now()
        for employee in self:
            attendance = employee.last_attendance_id
            if employee.attendance_state == 'checked_in':
                breakObj = self.env['hr.attendance.break.and.resume'].sudo().search([
                    ('attendance_id', '=', attendance.id),
                    ('break_time', '!=', False)
                ], limit=1, order='create_date desc')

                if employee.attendance_break_state == 'break' and breakObj.break_time:
                    breakObj.write({
                        'resume_time': action_date,
                        'attendance_break_state': 'resume',
                    })
                else:
                    vals = {
                        'attendance_id': attendance.id,
                        'employee_id': employee.id,
                        'break_time': action_date,
                        'attendance_break_state': 'break',
                    }
                    if reason_id:
                        vals['reason_id'] = reason_id
                    self.env['hr.attendance.break.and.resume'].create(vals)
        return True