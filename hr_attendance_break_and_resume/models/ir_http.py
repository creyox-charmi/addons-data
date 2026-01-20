from odoo import models
from odoo.http import request

class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super(Http, self).session_info()
        if self.env.user.has_group('base.group_user'):
            company = self.env.company
            result['hr_attendance_break_and_resume'] = company.hr_attendance_break_and_resume
        return result