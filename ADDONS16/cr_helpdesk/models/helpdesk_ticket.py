# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError
from pkg_resources import require


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Helpdesk Ticket"

    stage_id = fields.Many2one(
        "helpdesk.stage",
        string="State",
        default=lambda self: self._default_stage(),
        group_expand="_group_expand_stage_id",
        tracking=True,
    )
    priority = fields.Selection(
        [("0", "Low"), ("1", "Medium"), ("2", "Not Urgent"), ("3", "Urgent")]
    )
    name = fields.Char(string="Ticket Number", readonly=True, default=_("New"))
    contact_name = fields.Char(string="Contact Name", tracking=True, required=True)
    email = fields.Char(string="Email", tracking=True, required=True)
    so_number = fields.Char(string="Order Number", tracking=True)
    ticket_type = fields.Selection(
        [
            ("technical", "Technical support with purchased app"),
            ("billing", "Billing"),
            ("customize", "New Customization"),
            ("demo_request", "Demo Request"),
            ("migrate", "Migration"),
            ("enquiry", "Enquiry"),
        ],
        string="Ticket Type",
        tracking=True,
        required=True,
    )
    module_tech_name = fields.Many2one(
        "cr.odoo.apps", string="Module Technical Name", tracking=True, required=True
    )
    version = fields.Many2one(
        "cr.versions.odoo", string="Version", tracking=True, required=True
    )
    edition = fields.Selection(
        [("community", "Community"), ("enterprise", "Enterprise")],
        string="Edition",
        tracking=True,
        required=True,
    )
    odoo_platform = fields.Char(string="Odoo Platform", tracking=True)
    skype = fields.Char(string="Skype Id", tracking=True)
    mobile = fields.Char(string="Contact Number", tracking=True)
    message = fields.Html(string="Message", required=True)
    company_id = fields.Many2one("res.company", string="Company")
    user_id = fields.Many2one("res.users", string="Assignees")
    app_id = fields.Many2one("cr.odoo.apps", string="App Id")
    email_from = fields.Char(
        string="Email From", default=lambda self: self._get_default_email_from()
    )

    @api.model
    def _get_default_email_from(self):
        # Use ir.config_parameter to get the smtp_user
        return self.env["ir.config_parameter"].sudo().get_param("mail.smtp_user")

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        """Ensure all stages are displayed in the kanban view."""
        return self.env["helpdesk.stage"].search([], order=order)

    @api.model
    def create(self, vals):
        # Generate the sequence number only if it's not provided
        if vals.get("name", _("New")) == _("New"):
            current_year = datetime.now().year
            year = str(current_year)[-2:]
            sequence_number = self.env["ir.sequence"].next_by_code("helpdesk.ticket")
            vals["name"] = f"T{year}{sequence_number}"
        return super(HelpdeskTicket, self).create(vals)

    def copy(self, default=None):
        default = dict(default or {})
        # Generate a new sequence number for the copied record
        current_year = datetime.now().year
        year = str(current_year)[-2:]
        sequence_number = self.env["ir.sequence"].next_by_code("helpdesk.ticket")
        default["name"] = f"T{year}{sequence_number}"
        return super(HelpdeskTicket, self).copy(default)

    def unlink(self):
        # Check if the current user is part of the group
        if not self.env.user.has_group("cr_helpdesk.group_admin_helpdesk"):
            raise AccessError(
                "You do not have permission to delete this record. If this action is required to be performed, Please contact the system administrator."
            )
        return super(HelpdeskTicket, self).unlink()

    @api.model
    def _default_stage(self):
        """
        Get the default stage Draft having id = 1
        """
        draft_stage = self.env["helpdesk.stage"].search(
            [("name", "=", "Draft")], limit=1
        )
        if draft_stage:
            return draft_stage.id

    def message_post(self, **kwargs):
        res = super(HelpdeskTicket, self).message_post(**kwargs)

        # Check if 'email_to' is set
        if self.email:
            mail_server = self.env["ir.mail_server"].sudo().search([], limit=1)

            if mail_server:
                email_from = mail_server.smtp_user

            mail_values = {
                "subject": f"Message regarding Ticket {self.name}",
                "email_from": email_from,
                "email_to": self.email,
                "body_html": kwargs.get("body", ""),
            }
            # Send email
            self.env["mail.mail"].create(mail_values).send()

        return res
