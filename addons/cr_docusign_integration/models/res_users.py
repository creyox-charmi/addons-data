# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import requests
import base64
import hashlib
import random
import string

class ResUser(models.Model):
    _inherit = 'res.users'

    cr_app_name = fields.Char(string='App Name')
    cr_account_type = fields.Selection(
        [('developer', 'Developer'), ('production', 'Production')],
         string='Account Type')
    cr_integration_key = fields.Char(string='Integration Key')
    cr_secret_key = fields.Char(string='Secret Key')
    cr_access_token = fields.Char(string='Access Token')
    cr_account_id = fields.Char(string='Account ID')
    cr_auth_var_code = fields.Char()
    cr_redirect_url = fields.Char(string='Redirect Url')
    cr_auth_url = fields.Char(string='Auth URL')
    cr_token_url = fields.Char(string='Token URL')
    cr_user_info_url = fields.Char(string='User Info URL')
    cr_use_pkce = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        default='yes',
        string='Use PKCE'
    )

    @api.onchange('cr_account_type')
    def onchange_account_type(self):
        """Update URLs based on the selected account type."""
        if self.cr_account_type == 'developer':
            self.cr_auth_url = 'https://account-d.docusign.com/oauth/auth'
            self.cr_token_url = 'https://account-d.docusign.com/oauth/token'
            self.cr_user_info_url = 'https://account-d.docusign.com/oauth/userinfo'
        else:
            self.cr_auth_url = 'https://account.docusign.com/oauth/auth'
            self.cr_token_url = 'https://account.docusign.com/oauth/token'
            self.cr_user_info_url = 'https://account.docusign.com/oauth/userinfo'


    def open_docusign_auth(self):
        """Generate the authorization URL for DocuSign authentication."""
        if self.cr_use_pkce == 'yes':
            code_verifier, code_challenge = self.generate_code_verifier_and_challenge()
            self._set_code_verifier(code_verifier)
            params = {
                'response_type': 'code',
                'scope': 'signature',
                'client_id': self.cr_integration_key,
                'redirect_uri':self.cr_redirect_url,
                'code_challenge_method': 'S256',
                'code_challenge': code_challenge,
                'state': 'random_state_string',
            }
        else:
            params = {
                'response_type': 'code',
                'scope': 'signature',
                'client_id': self.cr_integration_key,
                'redirect_uri':self.cr_redirect_url,
                'state': 'random_state_string',
            }
        auth_url = requests.Request('GET', self.cr_auth_url, params=params).prepare().url
        print('self.cr_auth_url : ', self.cr_auth_url)
        print('auth_url : ',auth_url)
        return {
            'type': 'ir.actions.act_url',
            'url': auth_url,
            'target': 'self',
        }

    def _set_code_verifier(self, code_verifier):
        """Store the code verifier in a model field or temporary storage."""
        self.cr_auth_var_code = code_verifier

    def handle_authorization_code(self, authorization_code=None):
        """Handle the authorization code manually and exchange it for an access token."""
        if authorization_code:
            self.cr_auth_var_code = authorization_code
            token_info = self.get_access_token()

            if 'error' in token_info:
                raise ValidationError(f"Failed to get access token: {token_info['error']}")

            user_info = self.get_user_info(token_info.get('access_token'))

            if 'error' in user_info:
                raise ValidationError(f"Failed to fetch user info: {user_info['error']}")

            if 'account_id' in user_info:
                self.cr_account_id = user_info['account_id']
        else:
            raise ValidationError("No authorization code provided.")

    def generate_code_verifier_and_challenge(self):
        """Generate a PKCE code verifier and code challenge."""
        code_verifier = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()).decode().rstrip('=')
        return code_verifier, code_challenge

    def get_access_token(self):
        """Retrieve the access token using the authorization code."""
        if not self.cr_token_url:
            raise ValidationError("Token URL is not set.")

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'authorization_code',
            'code': self.cr_auth_var_code,
            'redirect_uri': self.cr_redirect_url,
            'client_id': self.cr_integration_key,
            'client_secret': self.cr_secret_key,
        }

        if self.cr_use_pkce == 'yes':
            data['code_verifier'] = self.cr_auth_var_code

        response = requests.post(self.cr_token_url, headers=headers, data=data)
        self.cr_access_token=response.json().get('access_token')
        return response.json()

    def send_token_reminder(self):
        """Send a reminder email to regenerate the access token."""

        subject = _('Reminder: Regenerate Your Access Token')
        body_html = _(
            '<p>Dear User,</p>'
            '<p>Your access token will expire soon. Please regenerate it to avoid any disruptions.</p>'
            '<p>Click the button "Get Login With Docusign Account" to renew the token.</p>'
            '<p>Thank you!</p>'
        )

        users_with_token = self.env['res.users'].search([('cr_access_token', '!=', False)])

        for user in users_with_token:
            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': user.email,
            }

            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

    def get_user_info(self, access_token):
        """Fetch user information from the API using the provided access token."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.cr_user_info_url, headers=headers)

        if response.status_code == 200:
            self.cr_account_id = response.json().get('accounts', [{}])[0].get('account_id')
            return response.json()
        else:
            raise ValidationError("Failed to fetch user info, status code: {}".format(response.status_code))