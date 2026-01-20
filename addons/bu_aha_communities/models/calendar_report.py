# Copyright 2022 Yves Goldberg (Ygol InternetWork)
# Part of module bu_aha_communities. See LICENSE file for
# full copyright and licensing details.

from odoo import api, fields, models
class CalendarReport(models.Model):
    _name = "calendar.report"
    _description = "Calendar Report"
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner',required=True)
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            self.phone = self.partner_id.phone
            self.mobile = self.partner_id.mobile
            self.email = self.partner_id.email
        else:
            self.phone = False
            self.mobile = False
            self.email = False

