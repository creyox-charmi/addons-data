# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    is_cancelled = fields.Boolean(string='Is Cancelled', default=False)

    def action_cancel_message(self):
        self.ensure_one()
        self.write({'is_cancelled': True})
        return {'type': 'ir.actions.client', 'tag': 'reload'}