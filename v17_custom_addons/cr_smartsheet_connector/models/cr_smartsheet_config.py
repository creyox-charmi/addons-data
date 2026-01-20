from odoo import models, fields, api,_
import requests
from odoo.http import request
from datetime import datetime
import time
from odoo.exceptions import UserError

class SmartsheetConfig(models.Model):
    _name = 'cr.smartsheet.config'
    _description = 'Smartsheet Configuration'
    _rec_name='cr_name'

    cr_europe_region = fields.Boolean(string='Europe Region')
    cr_name = fields.Char(string="Configuration Name", required=True, default="Smartsheet Integration")
    cr_client_id = fields.Char(string="Client ID", required=True)
    cr_client_secret = fields.Char(string="Client Secret", required=True)
    cr_redirect_uri = fields.Char(string="Redirect URI", default=lambda self: self.generate_url())
    cr_access_token = fields.Char(string='Access Token')
    cr_refresh_token = fields.Char(string='Refresh Token')
    cr_expires_in = fields.Datetime(string='Access Token Expires')
    cr_logs_ids = fields.One2many(
        "cr.processing.log", "cr_conf_id", string="Logs"
    )
    cr_import_contacts = fields.Boolean('Import Contacts')
    cr_import_image = fields.Boolean('Import Contact Image')
    cr_auto_contact=fields.Boolean('Auto Import Contacts')
    cr_import_scheduled_units = fields.Selection(
        [
            ("hours", "Hours"),
            ("minutes", "Minute"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Import Cron Units",
        default="hours",
    )
    cr_import_cron_value = fields.Integer(
        string="Import Cron Value",
    )
    cr_cron_job_id = fields.Many2one(
        "ir.cron", string="Scheduled Action", readonly=True
    )
    cr_import_user=fields.Boolean('Import Users')
    cr_import_user_image = fields.Boolean('Import User Image')
    def create_schedule_action(self):
        """
        Create a new scheduled action (cron job) for importing contacts.
        """
        if not self.cr_import_cron_value or not self.cr_import_scheduled_units:
            raise UserError("Please set both Cron Value and Cron Units.")

        if self.cr_cron_job_id:
            raise UserError("A scheduled action already exists. Please update or delete it first.")

        cron = self.env["ir.cron"].create({
            "name": f"Smartsheet Contact Import - {self.id}",
            "model_id": self.env["ir.model"]._get(self._name).id,
            "state": "code",
            "code": f"model.schedule_import({self.id})",
            "interval_number": self.cr_import_cron_value,
            "interval_type": self.cr_import_scheduled_units,
            "numbercall": -1,
            "doall": False,
        })

        self.cr_cron_job_id = cron.id

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": "Scheduled action created successfully!",
                "sticky": False,
            },
        }

    def update_schedule_action(self):
        """
        Update the existing scheduled action (cron job) with new values.
        """
        if not self.cr_cron_job_id:
            raise UserError("No scheduled action exists. Please create one first.")

        self.cr_cron_job_id.write({
            "interval_number": self.cr_import_cron_value,
            "interval_type": self.cr_import_scheduled_units,
        })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": "Scheduled action updated successfully!",
                "sticky": False,
            },
        }

    def delete_schedule_action(self):
        """
        Delete the existing scheduled action (cron job).
        """
        if not self.cr_cron_job_id:
            raise UserError("No scheduled action exists to delete.")

        self.cr_cron_job_id.unlink()
        self.cr_cron_job_id = False

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": "Scheduled action deleted successfully!",
                "sticky": False,
            },
        }

    def generate_url(self):
        """Retrieve the Odoo base URL."""
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        url = base + '/smartsheet/Auth/callback'
        return url

    def generate_token(self):
        """
        Generate a new API token by redirecting the user to Smartsheet's authorization page.
        """
        request.session['smartsheet_Record_id'] = self.id
        scopes = [
            "ADMIN_SHEETS","ADMIN_SIGHTS","ADMIN_USERS","ADMIN_WEBHOOKS","ADMIN_WORKSPACES","CREATE_SHEETS","CREATE_SIGHTS","DELETE_SHEETS","DELETE_SIGHTS","READ_CONTACTS","READ_EVENTS","READ_SHEETS","READ_SIGHTS","READ_USERS","SHARE_SHEETS","SHARE_SIGHTS","WRITE_SHEETS",
        ]
        scope_string = " ".join(scopes)
        if self.cr_europe_region:
            auth_url = (
                f"https://app.smartsheet.eu/b/authorize?"
                f"response_type=code&"
                f"client_id={self.cr_client_id}&"
                f"scope={scope_string}"
            )
        else:
            auth_url = (
                f"https://app.smartsheet.com/b/authorize?"
                f"response_type=code&"
                f"client_id={self.cr_client_id}&"
                f"scope={scope_string}"
            )
        return {
            'type': 'ir.actions.act_url',
            'url': auth_url,
            'target': 'self',
        }

    def exchange_code_for_token(self, authorization_code,id):
        """
        Exchange the authorization code for an access token and refresh token.
        """
        config = request.env['cr.smartsheet.config'].sudo().browse(int(id))
        if config.cr_europe_region:
            token_url = "https://api.smartsheet.eu/2.0/token"
        else:
            token_url = "https://api.smartsheet.com/2.0/token"
        payload = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": config.cr_redirect_uri,
            "client_id": config.cr_client_id,
            "client_secret": config.cr_client_secret,
        }

        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            token_data = response.json()
            expires_at = int(time.time()) + token_data.get('expires_in', 0)
            expires_at_datetime = datetime.utcfromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')

            config.write({
                'cr_access_token': token_data.get('access_token'),
                'cr_refresh_token': token_data.get('refresh_token'),
                'cr_expires_in': expires_at_datetime,
            })
            return request.render("cr_smartsheet_connector.success_redirect_template")
        else:
            raise Exception(f"Error exchanging code for token: {response.text}")

    def refresh_token(self):
        """
        Refresh the access token using the refresh token.
        """
        if not self.cr_refresh_token:
            raise Exception("No refresh token available.")
        if self.cr_europe_region:
            token_url = "https://api.smartsheet.eu/2.0/token"
        else:
            token_url = "https://api.smartsheet.com/2.0/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.cr_refresh_token,
            "client_id": self.cr_client_id,
            "client_secret": self.cr_client_secret,
        }

        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            token_data = response.json()
            expires_at = int(time.time()) + token_data.get('expires_in', 0)
            expires_at_datetime = datetime.utcfromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')

            self.write({
                'cr_access_token': token_data.get('access_token'),
                'cr_refresh_token': token_data.get('refresh_token'),
                'cr_expires_in': expires_at_datetime,
            })
            self.env["bus.bus"]._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {
                    "type": "success",
                    "title": _("Token"),
                    "message": _("Your Access Token Regenerated Successfully."),
                    "sticky": True,
                },
            )
        else:
            raise Exception(f"Error refreshing token: {response.text}")

    def import_contact(self):
        id=self.id
        self.env['cr.data.config'].sudo().import_contacts(id)

    def schedule_import(self,id):
        self.env['cr.data.config'].sudo().import_contacts(id)

    def import_user(self):
        id = self.id
        self.env['cr.data.config'].sudo().import_user(id)

    def schedule_import_user(self,id):
        self.env['cr.data.config'].sudo().import_user(id)