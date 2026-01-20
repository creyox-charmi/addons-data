# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api

class HrAttendanceBreakAndResume(models.Model):
    _inherit = 'hr.attendance.break.and.resume'

    reason_id = fields.Many2one('hr.attendance.break.reason', string='Reason', ondelete='restrict', required=True)
    reason_name = fields.Char(related='reason_id.name', string='Reason Name', store=True, readonly=True)

    @api.depends('break_time', 'resume_time', 'reason_id.name')
    def _get_formatted_time(self):
        super(HrAttendanceBreakAndResume, self)._get_formatted_time()
        for rec in self:
            if rec.reason_id and rec.formatted_time:
                rec.formatted_time = f"{rec.formatted_time} ({rec.reason_id.name})"

    @api.model
    def create(self, vals):
        if 'reason_name' in vals and not vals.get('reason_id'):
            reason = self.env['hr.attendance.break.reason'].search([
                ('name', '=ilike', vals['reason_name']),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            if not reason:
                reason = self.env['hr.attendance.break.reason'].create({
                    'name': vals['reason_name'],
                    'company_id': self.env.company.id
                })
            vals['reason_id'] = reason.id
        return super(HrAttendanceBreakAndResume, self).create(vals)