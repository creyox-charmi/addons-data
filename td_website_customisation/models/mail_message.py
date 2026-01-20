# -*- coding: utf-8 -*-

from odoo import models, fields


class MailMessage(models.Model):
    _inherit = 'mail.message'

    is_read_by_blog_author = fields.Boolean(
        string='Read by Blog Author',
        default=False,
        help="Indicates if the blog post author has read this message"
    )
    read_by_partner_ids = fields.Many2many(
        'res.partner',
        'mail_message_read_partner_rel',  # <- custom relation table name
        'message_id',  # <- column for mail.message
        'partner_id',  # <- column for res.partner
        string='Read by Partners',
        help='Partners who have read this message'
    )
    portal_read_partner_ids = fields.Many2many(
        'res.partner',
        'mail_message_portal_read_rel',
        'message_id',
        'partner_id',
        string='Portal Read By'
    )
    is_portal_reply = fields.Boolean(string='Is Portal Reply', default=False)
    portal_reply_body = fields.Html(string='Portal Reply Body')

    def mark_as_read_by_partner(self, partner_id):
        """Mark message as read by specific partner"""
        self.ensure_one()
        partner = self.env['res.partner'].browse(partner_id)
        if partner and partner not in self.portal_read_partner_ids:
            self.write({'portal_read_partner_ids': [(4, partner_id)]})

    def is_read_by_partner(self, partner_id):
        """Check if message is read by specific partner"""
        self.ensure_one()
        return partner_id in self.portal_read_partner_ids.ids