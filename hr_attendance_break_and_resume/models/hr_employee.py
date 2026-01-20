from odoo import models, fields, api, _
from odoo.fields import Datetime

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"
        
    attendance_break_state = fields.Selection(selection=[
        ('break', 'Break'),
        ('resume', 'Resume')
        ], string="Attendance Break Status", 
        compute='_compute_attendance_break_state',
        default='resume')

    @api.depends('last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id')
    def _compute_attendance_break_state(self):        
        for employee in self:
            attendance = employee.last_attendance_id.sudo()
            if attendance.break_ids:
                breakObj = self.env['hr.attendance.break.and.resume'].search([('attendance_id','=',attendance.id)], limit=1, order='create_date desc')
                employee.attendance_break_state = breakObj.attendance_break_state if breakObj else 'resume'
            else:
                employee.attendance_break_state = 'resume'

    def attendance_break_resume_action(self):        
        self.ensure_one()
        action_date = Datetime.now()
        for employee in self:
            attendance = employee.last_attendance_id
            if employee.attendance_state == 'checked_in':
                breakObj = self.env['hr.attendance.break.and.resume'].sudo().search([('attendance_id','=',attendance.id), ('break_time','!=',False)], limit=1, order='create_date desc')

                if employee.attendance_break_state == 'break' and breakObj.break_time:
                    breakObj.write({
                        'resume_time': action_date,
                        'attendance_break_state': 'resume',
                    })
                else:
                    self.env['hr.attendance.break.and.resume'].create({
                        'attendance_id': attendance.id,
                        'employee_id': employee.id,
                        'break_time': action_date,
                        'attendance_break_state': 'break',
                    })
        return True