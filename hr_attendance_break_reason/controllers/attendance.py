# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import http
from odoo.http import request
from odoo.addons.hr_attendance_break_and_resume.controllers.attendance import HrAttendance

class HrAttendanceBreakReason(HrAttendance):

    @http.route('/hr_attendance/attendance_break_resume_action', type="json", auth="public")
    def ge_attendance_break_state(self, employee, reason_id=None, token=None):
        if employee:
            employee = request.env['hr.employee'].sudo().search([['id', '=', int(employee)]])
            employee.attendance_break_resume_action(reason_id=reason_id)
            return employee.attendance_break_state

    @http.route('/hr_attendance/get_break_reasons', type="json", auth="public")
    def get_break_reasons(self):
        reasons = request.env['hr.attendance.break.reason'].sudo().search([
            ('company_id', '=', request.env.company.id)
        ])
        return [{'id': r.id, 'name': r.name} for r in reasons]

    @http.route('/hr_attendance/create_break_reason', type="json", auth="public")
    def create_break_reason(self, name, token=None):
        reason = request.env['hr.attendance.break.reason'].sudo().create({
            'name': name,
            'company_id': request.env.company.id
        })
        return reason.id

    @staticmethod
    def _get_employee_info_response(employee):
        rslt = super(HrAttendanceBreakReason, HrAttendanceBreakReason)._get_employee_info_response(employee)
        rslt['attendance_break_state'] = employee.attendance_break_state
        return rslt