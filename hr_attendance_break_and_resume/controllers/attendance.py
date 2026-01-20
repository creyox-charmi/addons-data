from odoo import http, _
from odoo.http import request
import datetime
from odoo.addons.hr_attendance.controllers.main import HrAttendance as HrAttendance

class HrAttendance(HrAttendance):

    @staticmethod
    def _get_user_attendance_data(employee):
        rslt = super(HrAttendance, HrAttendance)._get_user_attendance_data(employee)
        rslt['attendance_break_state'] = employee.attendance_break_state or 'break'
        return rslt
    
    @staticmethod
    def _get_employee_info_response(employee):
        rslt = super(HrAttendance, HrAttendance)._get_employee_info_response(employee)
        rslt['attendance']['id'] = employee.last_attendance_id.id or False
        return rslt
    
    @http.route('/hr_attendance/get_attendance_break_state', type="json", auth="public")
    def get_attendance_break_state(self, token, employee):
        company = self._get_company(token)
        if company:
            employee = request.env['hr.employee'].sudo().search([('id', '=', int(employee)), ('company_id', '=', company.id)], limit=1)
            if employee:
                return self._get_employee_info_response(employee)
        return {}
    
    @http.route('/hr_attendance/attendance_break_resume_action', type="json", auth="public")
    def ge_attendance_break_state(self, employee):
        if employee:
            employee = request.env['hr.employee'].sudo().search([['id', '=', int(employee)]])
            employee.attendance_break_resume_action()
            return employee.attendance_break_state
    
    @http.route('/hr_attendance/attendance_res_config', type="json", auth="public",)
    def attendance_res_config(self, token):
        company = self._get_company(token)
        conf = {}
        if company:
            conf['hr_attendance_break_and_resume_k'] = company.hr_attendance_break_and_resume_k
        return conf