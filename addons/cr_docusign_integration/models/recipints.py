# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api

class Recipients(models.Model):
    _name='cr.recipients'

    cr_partner = fields.Many2one('res.partner',string='Partner')
    cr_name=fields.Char(string='Name',compute='compute_name',store=True)
    cr_routing_order=fields.Integer()
    cr_has_signed = fields.Boolean()
    cr_email = fields.Char(string='Email',compute='compute_email',store=True,readonly=False)
    cr_send_status = fields.Selection( [
         ('draft','draft'),
         ('sent','Sent'),
         ('complete','Completed')],default='draft',string='Send Status')
    cr_sign_status = fields.Selection([
        ('unsigned', 'Unsigned'),
        ('signed', 'Signed'),
    ], string='Sign Status', default='unsigned')
    cr_unsigned_attachments= fields.Binary(string='Unsigned attachments')
    cr_signed_attachments= fields.Binary(string='Signed attachments')
    cr_sign=fields.Many2one("cr.signature")

    @api.depends('cr_partner')
    def compute_email(self):
        """Compute the email based on the associated partner."""
        self.cr_email=self.cr_partner.email

    @api.depends('cr_partner')
    def compute_name(self):
        """Compute the name based on the associated partner."""
        for record in self:
            record.cr_name = record.cr_partner.name
