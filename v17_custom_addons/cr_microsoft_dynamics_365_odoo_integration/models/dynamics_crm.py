# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

import logging
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class DynamicsCrm(models.Model):
    _name = 'cr.dynamics.crm'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Dynamics 365 CRM Integration"
    _order = 'id desc'

    name = fields.Char(required=True, index=True)
    domain = fields.Char('Domain', required=True, help="e.g., org15b72481")
    region = fields.Char('Region', required=True, default='crm8', help="e.g., crm8 for Southeast Asia")
    client_id = fields.Char('Client ID', required=True, help="Azure AD Application ID")
    client_secret = fields.Char('Client Secret', required=True, help="Azure AD Client Secret")
    tenant_id = fields.Char('Tenant ID', required=True, help="e.g., 8f417b23-30ff-4218-8969-d5780063a5e3")
    redirect_uri = fields.Char('Redirect URI', required=True, help="e.g., http://localhost:8069/dynamics/callback")
    scope = fields.Char('Scope', compute='_compute_scope', store=True, readonly=False, help="OAuth scope for Dynamics 365")
    auth_code = fields.Char('Authorization Code', help="Paste the code from the Microsoft redirect URL here")
    access_token = fields.Char('Access Token', readonly=True)
    refresh_token = fields.Char('Refresh Token', readonly=True)
    token_expiry = fields.Datetime('Token Expiry', readonly=True)

    @api.depends('domain', 'region')
    def _compute_scope(self):
        """Dynamically compute scope based on domain and region."""
        for record in self:
            if record.domain and record.region:
                record.scope = f"https://{record.domain}.api.{record.region}.dynamics.com/user_impersonation offline_access"
            elif not record.scope:  # Fallback if not set
                record.scope = "https://org15b72481.api.crm8.dynamics.com/user_impersonation offline_access"

    @api.model
    def create(self, vals):
        """Ensure scope is computed on create."""
        record = super(DynamicsCrm, self).create(vals)
        if not record.scope:
            record._compute_scope()
        return record

    def write(self, vals):
        """Ensure scope is recomputed on write."""
        res = super(DynamicsCrm, self).write(vals)
        if 'domain' in vals or 'region' in vals:
            self._compute_scope()
        return res

    def _get_auth_url(self):
        """Generate the authorization URL with correct scope."""
        if not self.scope:
            self._compute_scope()  # Force scope computation if missing
        base_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'state': str(self.id),
        }
        auth_url = f"{base_url}?{urlencode(params)}"
        _logger.info(f"Generated authorization URL: {auth_url}")
        return auth_url

    def _get_token_url(self):
        """Return the token endpoint URL."""
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

    def action_authorize(self):
        """Redirect user to Microsoft login page and prompt for code."""
        auth_url = self._get_auth_url()
        _logger.info(f"Redirecting user to: {auth_url}")
        self.message_post(body=_("Please visit this URL in your browser: %s\nAfter signing in, copy the 'code' parameter from the redirect URL (e.g., 'code=0.A...') and paste it into the 'Authorization Code' field, then click 'Process Code'.") % auth_url)
        return {
            'type': 'ir.actions.act_url',
            'url': auth_url,
            'target': 'new',
        }

    def action_process_code(self):
        """Process the manually entered authorization code to fetch tokens."""
        if not self.auth_code:
            raise ValidationError(_("Please enter the authorization code from the Microsoft redirect URL."))
        self.get_access_token(code=self.auth_code)
        self.auth_code = False  # Clear the code after processing
        _logger.info(f"Authorization code processed successfully for record {self.id}.")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cr.dynamics.crm',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def get_access_token(self, code=None):
        now = fields.Datetime.now()
        if self.access_token and self.token_expiry and self.token_expiry > now:
            _logger.info("Using cached access token.")
            return self.access_token
        elif self.refresh_token and (not self.token_expiry or self.token_expiry <= now):
            _logger.info("Access token expired, attempting to refresh.")
            # Refresh logic already exists in the method
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            token_url = self._get_token_url()
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'scope': self.scope,
            }
            response = requests.post(token_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()
            self.write({
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', self.refresh_token),
                'token_expiry': fields.Datetime.to_string(
                    datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))),
            })
            _logger.info(f"Token refreshed successfully: {token_data}")
            return self.access_token
        elif code:
            # Existing code logic
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            token_url = self._get_token_url()
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri,
                'scope': self.scope,
            }
            response = requests.post(token_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()
            self.write({
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'token_expiry': fields.Datetime.to_string(
                    datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))),
            })
            _logger.info(f"Token fetched successfully: {token_data}")
            return self.access_token
        else:
            raise ValidationError(_("No valid access token or refresh token available. Please reauthorize the app."))

    def _fetch_entity(self, entity_type):
        """Fetch data from Dynamics 365 Web API using Bearer token."""
        access_token = self.get_access_token()
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Accept': 'application/json',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
        }
        url = f"https://{self.domain}.api.{self.region}.dynamics.com/api/data/v9.2/{entity_type}"
        _logger.info(f"Fetching {entity_type} from {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            _logger.info(f"Fetched {entity_type}: {len(data.get('value', []))} records")
            return data
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            _logger.error(f"API request failed: {error_msg}")
            raise ValidationError(_('API request failed: %s') % error_msg)
        except Exception as e:
            raise ValidationError(str(e))

    def action_get_contacts(self):
        data = self._fetch_entity('contacts')
        contacts = data.get('value', [])
        partner_vals = []
        for contact in contacts:
            partner_vals.append({
                'name': contact.get('fullname', 'Unknown'),
                'email': contact.get('emailaddress1'),
                'phone': contact.get('telephone1'),
                # 'source': 'dynamics_365',  # Add a custom field to track origin
            })
        self.env['res.partner'].create(partner_vals)
        self.message_post(body=_("Imported %s contacts from Dynamics 365.") % len(contacts))

    def action_get_accounts(self):
        """
        Fetch accounts from Dynamics 365 and sync them to Odoo as res.partner records.
        Maps account data to company partners, handles duplicates, and logs the process.
        """
        # Fetch accounts with specific fields using OData $select to optimize the response
        data = self._fetch_entity(
            'accounts?$select=accountid,name,telephone1,emailaddress1,websiteurl,description,address1_line1,address1_city,address1_stateorprovince,address1_postalcode,address1_country,fax,revenue,numberofemployees')
        accounts = data.get('value', [])

        # Reference to res.partner model
        partner_obj = self.env['res.partner']
        synced_count = 0

        # Process each account from the Dynamics 365 response
        for account in accounts:
            # Check for existing record using a custom Dynamics ID field (x_dynamics_id)
            existing = partner_obj.search([('x_dynamics_id', '=', account['accountid'])], limit=1)

            # Prepare values for res.partner based on Dynamics 365 data
            vals = {
                'name': account.get('name', 'Unknown'),  # Company name
                'phone': account.get('telephone1'),  # Primary phone
                'email': account.get('emailaddress1'),  # Primary email
                'website': account.get('websiteurl'),  # Website URL
                'comment': account.get('description'),  # Description as a note
                'street': account.get('address1_line1'),  # Street address
                'city': account.get('address1_city'),  # City
                'state_id': self.env['res.country.state'].search([
                    ('name', '=', account.get('address1_stateorprovince')),
                    ('country_id.code', '=', 'US')
                ], limit=1).id if account.get('address1_stateorprovince') else False,  # State (US-specific)
                'zip': account.get('address1_postalcode'),  # Postal code
                'country_id': self.env['res.country'].search([
                    ('name', '=', account.get('address1_country'))
                ], limit=1).id if account.get('address1_country') else False,  # Country
                # 'fax': account.get('fax'),  # Fax number
                'x_dynamics_id': account['accountid'],  # Custom field for Dynamics account ID
                'is_company': True,  # Mark as a company in Odoo
                # Optional additional fields
                'x_revenue': account.get('revenue'),  # Custom field for revenue
                'x_employee_count': account.get('numberofemployees'),  # Custom field for employee count
            }

            # Update or create the partner record
            if existing:
                existing.write(vals)
                action = "updated"
            else:
                partner_obj.create(vals)
                action = "created"
                synced_count += 1

            _logger.info(f"Account {account['accountid']} ({account.get('name', 'Unknown')}) {action} in Odoo.")

        # Post a message with the sync result
        self.message_post(body=_("Synced %s accounts from Dynamics 365 (%s new, %s updated).") % (
            len(accounts), synced_count, len(accounts) - synced_count))

        # Return an action to refresh the form view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cr.dynamics.crm',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def action_get_opportunities(self):
        # Fetch opportunities
        data = self._fetch_entity(
            'opportunities?$select=opportunityid,name,description,emailaddress,estimatedvalue,estimatedclosedate,'
            'createdon,modifiedon,statecode,statuscode,salesstagecode,closeprobability,'
            'customerneed,currentsituation,proposedsolution,budgetamount,actualclosedate,actualvalue,'
            '_parentaccountid_value,_parentcontactid_value,_customerid_value'
        )
        opportunities = data.get('value', [])
        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']
        synced_count = 0

        # Dynamically fetch stages by name or sequence
        stage_new = self.env['crm.stage'].search([('name', 'ilike', 'New')], order='sequence asc', limit=1)
        stage_proposition = self.env['crm.stage'].search([('name', 'ilike', 'Proposition')], order='sequence', limit=1)
        stage_negotiation = self.env['crm.stage'].search([('name', 'ilike', 'Negotiation')], order='sequence', limit=1)
        stage_won = self.env['crm.stage'].search([('name', 'ilike', 'Won')], limit=1)
        stage_lost = self.env['crm.stage'].search([('name', 'ilike', 'Lost')], limit=1)
        default_stage = self.env['crm.stage'].search([], order='sequence asc', limit=1)  # Fallback

        for opp in opportunities:
            existing = lead_obj.search([('x_dynamics_opportunity_id', '=', opp['opportunityid'])], limit=1)

            # Link to parent account or contact
            partner_id = False
            if opp.get('_customerid_value'):
                partner = partner_obj.search([('x_dynamics_id', '=', opp['_customerid_value'])], limit=1)
                if not partner:
                    partner = partner_obj.search([('x_dynamics_contact_id', '=', opp['_customerid_value'])], limit=1)
                if partner:
                    partner_id = partner.id

            # Map Dynamics statecode/statuscode to Odoo stage
            stage_id = False
            if opp.get('statecode') == 0:  # Open
                if opp.get('salesstagecode') == 1:  # Qualify
                    stage_id = stage_new.id if stage_new else default_stage.id
                elif opp.get('salesstagecode') == 2:  # Develop
                    stage_id = stage_proposition.id if stage_proposition else default_stage.id
                elif opp.get('salesstagecode') == 3:  # Propose
                    stage_id = stage_negotiation.id if stage_negotiation else default_stage.id
            elif opp.get('statecode') == 1:  # Won
                stage_id = stage_won.id if stage_won else default_stage.id
            elif opp.get('statecode') == 2:  # Lost
                stage_id = stage_lost.id if stage_lost else default_stage.id

            if not stage_id:
                stage_id = default_stage.id
                _logger.warning(
                    f"No matching stage for opportunity {opp['opportunityid']}. Using default: {default_stage.name}")

            # Convert date fields
            created_on = opp.get('createdon')
            if created_on:
                dt = datetime.strptime(created_on, '%Y-%m-%dT%H:%M:%SZ')
                created_on = fields.Datetime.to_string(dt)
            else:
                created_on = False

            estimated_close = opp.get('estimatedclosedate')
            if estimated_close:
                dt = datetime.strptime(estimated_close, '%Y-%m-%d')
                estimated_close = fields.Date.to_string(dt)
            else:
                estimated_close = False

            actual_close = opp.get('actualclosedate')
            if actual_close:
                dt = datetime.strptime(actual_close, '%Y-%m-%d')
                actual_close = fields.Date.to_string(dt)
            else:
                actual_close = False

            # Prepare values
            vals = {
                'name': opp.get('name', 'Unnamed Opportunity'),
                'type': 'opportunity',
                'description': '\n'.join(filter(None, [
                    opp.get('description'),
                    f"Customer Need: {opp.get('customerneed')}" if opp.get('customerneed') else None,
                    f"Current Situation: {opp.get('currentsituation')}" if opp.get('currentsituation') else None,
                    f"Proposed Solution: {opp.get('proposedsolution')}" if opp.get('proposedsolution') else None,
                ])),
                'email_from': opp.get('emailaddress'),
                # 'planned_revenue': opp.get('estimatedvalue', 0.0),
                'date_deadline': estimated_close,
                'date_open': created_on,
                'date_closed': actual_close,
                'probability': opp.get('closeprobability', 0),
                'partner_id': partner_id if partner_id else False,
                'x_dynamics_opportunity_id': opp['opportunityid'],
                'stage_id': stage_id,
                'x_budget_amount': opp.get('budgetamount', 0.0),
                'x_actual_value': opp.get('actualvalue', 0.0),
            }

            # Create or update
            if existing:
                existing.write(vals)
                action = "updated"
            else:
                lead_obj.create(vals)
                action = "created"
                synced_count += 1

            _logger.info(f"Opportunity {opp['opportunityid']} ({opp.get('name', 'Unnamed')}) {action} in Odoo CRM.")

        self.message_post(body=_("Synced %s opportunities from Dynamics 365 (%s new, %s updated).") % (
            len(opportunities), synced_count, len(opportunities) - synced_count))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cr.dynamics.crm',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def action_get_leads(self):
        """
        Fetch leads from Dynamics 365 and sync them to Odoo crm.lead.
        Maps key fields, handles parent accounts, and tracks status.
        """
        data = self._fetch_entity('leads')
        leads = data.get('value', [])
        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']
        synced_count = 0

        for lead in leads:
            # Check for existing lead by Dynamics lead ID
            existing = lead_obj.search([('x_dynamics_lead_id', '=', lead['leadid'])], limit=1)

            # Prepare contact name and lead name
            contact_name = lead.get('fullname') or ' '.join(
                filter(None, [lead.get('firstname'), lead.get('lastname')])) or 'Unknown'
            lead_name = lead.get('subject') or lead.get('companyname') or contact_name

            # Link to parent account if synced as res.partner
            parent_account_id = False
            if lead.get('_parentaccountid_value'):
                parent_account = partner_obj.search([('x_dynamics_account_id', '=', lead['_parentaccountid_value'])],
                                                    limit=1)
                if parent_account:
                    parent_account_id = parent_account.id

            # Map Dynamics status to Odoo stage (customize as needed)
            stage_id = False
            if lead.get('statecode') == 0 and lead.get('statuscode') == 1:
                stage_id = self.env.ref('crm.stage_lead1').id  # New
            elif lead.get('statecode') == 1:  # Qualified or closed
                stage_id = self.env.ref('crm.stage_lead4').id  # Won
            elif lead.get('statecode') == 2:  # Disqualified
                stage_id = self.env.ref('crm.stage_lead5').id  # Lost

            # Convert Dynamics ISO 8601 datetime to Odoo format
            created_on = lead.get('createdon')
            if created_on:
                # Parse ISO 8601 format and convert to Odoo-compatible string
                dt = datetime.strptime(created_on, '%Y-%m-%dT%H:%M:%SZ')
                created_on = fields.Datetime.to_string(dt)
            else:
                created_on = False

            # Prepare values for crm.lead
            vals = {
                'name': lead_name,  # Use subject or companyname as lead title
                'contact_name': contact_name if lead.get('firstname') or lead.get('lastname') else False,
                'email_from': lead.get('emailaddress1'),
                'phone': lead.get('telephone1') or lead.get('mobilephone'),
                'mobile': lead.get('mobilephone'),
                'description': lead.get('description'),
                'street': lead.get('address1_line1'),
                'city': lead.get('address1_city'),
                'state_id': self.env['res.country.state'].search([
                    ('name', '=', lead.get('address1_stateorprovince')),
                    ('country_id.code', '=', 'US')
                ], limit=1).id if lead.get('address1_stateorprovince') else False,
                'zip': lead.get('address1_postalcode'),
                'country_id': self.env['res.country'].search([
                    ('name', '=', lead.get('address1_country'))
                ], limit=1).id if lead.get('address1_country') else False,
                'website': lead.get('websiteurl'),
                # 'job_position': lead.get('jobtitle'),
                # 'planned_revenue': lead.get('revenue', 0.0),  # Revenue as potential value
                # 'expected_revenue': lead.get('budgetamount', 0.0),  # Budget as expected
                'type': 'lead',  # Start as lead; can change to 'opportunity'
                'partner_id': parent_account_id if parent_account_id else False,
                'x_dynamics_lead_id': lead['leadid'],  # Custom field for Dynamics ID
                'stage_id': stage_id if stage_id else self.env.ref('crm.stage_lead1').id,
                'date_open': created_on,  # Use the converted datetime
            }

            # Create or update the lead
            if existing:
                existing.write(vals)
                action = "updated"
            else:
                lead_obj.create(vals)
                action = "created"
                synced_count += 1

            _logger.info(f"Lead {lead['leadid']} ({lead_name}) {action} in Odoo CRM.")

        # Post sync summary
        self.message_post(body=_("Synced %s leads from Dynamics 365 (%s new, %s updated).") % (
            len(leads), synced_count, len(leads) - synced_count))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cr.dynamics.crm',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def action_get_campaigns(self):
        data = self._fetch_entity('campaigns')
        self.message_post(body=_("Fetched %s campaigns from Dynamics 365.") % len(data.get('value', [])))