# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.payment import utils as payment_utils
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    bigcommerce_store_id = fields.Many2one('bigcommerce.store', string="BigCommerce Store")
    bigcommerce_customer_id = fields.Integer("BigCommerce Customer ID")
    bigcommerce_company = fields.Char("Company")
    bigcommerce_group_id = fields.Integer("Customer Group ID")
    bigcommerce_notes = fields.Text("Notes")
    bigcommerce_registration_ip = fields.Char("Registration IP")
    bigcommerce_tax_exempt_category = fields.Char("Tax Exempt Category")
    bigcommerce_date_created = fields.Datetime("Date Created")
    bigcommerce_date_modified = fields.Datetime("Date Modified")
    bigcommerce_accepts_review_emails = fields.Boolean("Accepts Review Emails")
    bigcommerce_origin_channel_id = fields.Integer("Origin Channel ID")

    def action_update_customer_bigcommerce(self):
        self.ensure_one()

        store = self.bigcommerce_store_id
        if not store:
            raise UserError(_("This customer is not linked to any BigCommerce store."))

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials on the BigCommerce store."))

        if not self.bigcommerce_customer_id:
            raise UserError(_("This customer does not have a BigCommerce Customer ID."))

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers"

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Prepare payload as an array with one customer object including the required 'id' field
        payload = [{
            "id": self.bigcommerce_customer_id,
            "email": self.email or f"{self.id}@example.com",
            "first_name": self.name.split()[0] if self.name else "Unknown",
            "last_name": self.name.split()[-1] if self.name else "Customer",
            "company": self.bigcommerce_company or "",
            "phones": self.phone or "",
            "phone": self.phone or "",
            "notes": self.bigcommerce_notes or "",
            "tax_exempt_category": self.bigcommerce_tax_exempt_category or "",
            "customer_group_id": self.bigcommerce_group_id or 0,
            "registration_ip_address": self.bigcommerce_registration_ip or "",
            "accepts_product_review_abandoned_cart_emails": self.bigcommerce_accepts_review_emails,
        }]

        response = requests.put(url, headers=headers, json=payload)

        if response.status_code in [200, 204]:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Customer updated successfully in BigCommerce."),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            error_msg = response.text
            raise UserError(_("Failed to update customer in BigCommerce: %s") % error_msg)

    def action_export_to_bigcommerce(self):
        self.ensure_one()

        store = self.bigcommerce_store_id
        if not store:
            raise UserError(_("This customer is not linked to any BigCommerce store."))

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials on the linked BigCommerce store."))

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        customer_data = {
            "email": self.email or f"{self.id}@example.com",
            "first_name": self.name.split()[0] if self.name else "Unknown",
            "last_name": self.name.split()[-1] if self.name else "Customer",
            "company": self.bigcommerce_company or "",
            "phone": self.phone or "",
            "notes": self.bigcommerce_notes or "",
            "tax_exempt_category": self.bigcommerce_tax_exempt_category or "",
            "customer_group_id": self.bigcommerce_group_id or 0,
            "addresses": [
                {
                    "address1": self.street or "Unknown Street",
                    "city": self.city or "Unknown City",
                    "country_code": self.country_id.code if self.country_id else "US",
                    "first_name": self.name.split()[0] if self.name else "Unknown",
                    "last_name": self.name.split()[-1] if self.name else "Customer",
                    "phone": self.phone or "",
                    "postal_code": self.zip or "00000",
                    "state_or_province": self.state_id.name if self.state_id else "",
                }
            ],
            "accepts_product_review_abandoned_cart_emails": self.bigcommerce_accepts_review_emails,
            "origin_channel_id": self.bigcommerce_origin_channel_id or 1,
            "trigger_account_created_notification": True
        }

        # Create new customer (POST)
        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers"
        payload = [customer_data]
        response = requests.post(url, headers=headers, json=payload)

        def parse_datetime(dt_str):
            if not dt_str:
                return False
            if dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            dt_str = dt_str.replace('T', ' ')
            return fields.Datetime.to_datetime(dt_str)

        if response.status_code in [200, 201, 204]:
            data = response.json().get('data', [])
            if data:
                cust_data = data[0]
                self.write({
                    'bigcommerce_store_id': store.id,
                    'bigcommerce_customer_id': cust_data.get('id'),
                    'bigcommerce_date_created': parse_datetime(cust_data.get('date_created')),
                    'bigcommerce_date_modified': parse_datetime(cust_data.get('date_modified')),
                    'bigcommerce_company': cust_data.get('company'),
                    'bigcommerce_group_id': cust_data.get('customer_group_id'),
                    'bigcommerce_notes': cust_data.get('notes'),
                    'bigcommerce_registration_ip': cust_data.get('registration_ip_address'),
                })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Export Success"),
                    'message': _("Customer exported successfully to BigCommerce."),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("Failed to export customer: %s") % response.text)

    def action_delete_customer_from_bigcommerce(self):
        self.ensure_one()

        store = self.bigcommerce_store_id
        if not store:
            raise UserError(_("This customer is not linked to any BigCommerce store."))

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials on the linked BigCommerce store."))

        if not self.bigcommerce_customer_id:
            raise UserError(_("This customer does not have a BigCommerce customer ID."))

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
        }
        params = {
            "id:in": str(self.bigcommerce_customer_id)
        }

        response = requests.delete(url, headers=headers, params=params)
        if response.status_code in [204, 200]:
            self.write({
                'bigcommerce_customer_id': False,
                'bigcommerce_date_created': False,
                'bigcommerce_date_modified': False,
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Delete Success"),
                    'message': _("Customer deleted successfully from BigCommerce."),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("Failed to delete customer: %s") % response.text)

    def action_delete_customers_from_bigcommerce(self):
        """ Delete multiple customers from BigCommerce in batches """
        self.ensure_one()

        store = self
        if not store:
            raise UserError(_("No BigCommerce store found."))

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials on the BigCommerce store."))

        # Find customers linked to this store with bigcommerce_customer_id set
        customers = self.env['res.partner'].search([
            ('bigcommerce_store_id', '=', store.id),
            ('bigcommerce_customer_id', '!=', False)
        ])

        if not customers:
            raise UserError(_("No customers with BigCommerce IDs found for deletion."))

        import math

        batch_size = 10  # BigCommerce API limit
        total = len(customers)
        batches = math.ceil(total / batch_size)

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
        }

        for i in range(batches):
            batch_customers = customers[i * batch_size:(i + 1) * batch_size]
            customer_ids = [str(c.bigcommerce_customer_id) for c in batch_customers]
            params = {
                "id:in": ",".join(customer_ids)
            }

            response = requests.delete(url, headers=headers, params=params)
            if response.status_code not in [204, 200]:
                raise UserError(_("Failed to delete customers: %s") % response.text)

            # Clear BigCommerce fields on batch deleted customers
            batch_customers.write({
                'bigcommerce_customer_id': False,
                'bigcommerce_date_created': False,
                'bigcommerce_date_modified': False,
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Batch Delete Success"),
                'message': _(f"Deleted {total} customers from BigCommerce in {batches} batch(es)."),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_create_bigcommerce_customer_address(self):
        self.ensure_one()

        store = self.bigcommerce_store_id
        if not store:
            raise UserError(_("This customer is not linked to any BigCommerce store."))

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials on the linked BigCommerce store."))

        if not self.bigcommerce_customer_id:
            raise UserError(_("Customer does not have a linked BigCommerce customer ID."))

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers/addresses"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        first_name, last_name = payment_utils.split_partner_name(self.name)
        payload = [{
            "customer_id": self.bigcommerce_customer_id,
            "first_name": first_name if self.name else "Unknown",
            "last_name": last_name if self.name else "Customer",
            "company": self.company_id.name or "",
            "address1": self.street or "Unknown Street",
            "address2": self.street2 or "",
            "city": self.city or "Unknown City",
            "state_or_province": self.state_id.name if self.state_id else "",
            "postal_code": self.zip or "",
            "country_code": self.country_id.code if self.country_id else "US",
            "phone": self.phone or "",
            "address_type": "residential",  # or "commercial" based on your logic
            "form_fields": [],  # Optional: add any custom form fields here
        }]

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            data = response.json().get('data', [])

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Customer address created in BigCommerce."),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("Failed to create customer address: %s") % response.text)

    def action_update_bigcommerce_address(self):
        self.ensure_one()

        if not self.bigcommerce_store_id or not self.bigcommerce_store_id.access_token:
            raise UserError("Missing linked BigCommerce store or credentials.")

        store = self.bigcommerce_store_id

        if not self.bigcommerce_customer_id:
            raise UserError("This address is not linked to a customer with a BigCommerce ID.")

        first_name, last_name = payment_utils.split_partner_name(self.name)
        address_data = {
            "id": int(self.bigcommerce_customer_id),
            "first_name": first_name or self.parent_id.name.split()[0] if self.parent_id.name else "Unknown",
            "last_name": last_name or self.parent_id.name.split()[-1] if self.parent_id.name else "Customer",
            "company": self.company_id.name or self.parent_id.company_name or "",
            "address1": self.street or "Unknown Street",
            "address2": self.street2 or "",
            "city": self.city or "Unknown City",
            "state_or_province": self.state_id.name if self.state_id else "",
            "postal_code": self.zip or "",
            "country_code": self.country_id.code if self.country_id else "US",
            "phone": self.phone or self.parent_id.phone or "",
            "address_type": "residential",  # or "commercial"
            "form_fields": []
        }

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers/addresses"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.put(url, headers=headers, json=[address_data])
        if response.status_code not in [200, 201]:
            raise UserError(f"Failed to update address: {response.text}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Success",
                'message': "Address updated in BigCommerce.",
                'type': 'success',
                'sticky': False,
            }
        }

    def action_delete_bigcommerce_address(self):
        self.ensure_one()

        if not self.bigcommerce_customer_id:
            raise UserError(_("No BigCommerce Customer ID found on this record."))

        store = self.bigcommerce_store_id
        if not store or not store.access_token or not store.store_hash:
            raise UserError(_("Missing BigCommerce store or credentials."))

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v3/customers/addresses"
        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        params = {
            "id:in": self.bigcommerce_customer_id,
        }

        response = requests.delete(url, headers=headers, params=params)

        if response.status_code in [200, 204]:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Address deleted from BigCommerce."),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("Failed to delete address: %s") % response.text)
