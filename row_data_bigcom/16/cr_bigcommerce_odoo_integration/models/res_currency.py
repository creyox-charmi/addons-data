# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    bc_currency_id = fields.Integer("BigCommerce Currency ID", readonly=True)
    bc_name = fields.Char("Name")
    bigcommerce_store_id = fields.Many2one('bigcommerce.store', string="BigCommerce Store")
    bc_currency_code = fields.Char("BigCommerce Currency Code")
    bc_enabled = fields.Boolean("BigCommerce Enabled")
    bc_is_transactional = fields.Boolean("BigCommerce Transactional")
    bc_is_default = fields.Boolean("BigCommerce Default")
    bc_auto_update = fields.Boolean("BigCommerce Auto Update")
    bc_exchange_rate = fields.Float("BigCommerce Exchange Rate")
    bc_token = fields.Char("Currency Token")
    bc_token_location = fields.Selection([('left', 'Left'), ('right', 'Right')], string="Token Location")
    bc_decimal_places = fields.Integer("Decimal Places")
    bc_decimal_token = fields.Char("Decimal Token")
    bc_thousands_token = fields.Char("Thousands Token")
    bc_default_for_country_codes = fields.Char("Default For Countries")
    bc_country_iso2 = fields.Char("Country ISO2")
    bc_last_updated = fields.Datetime("Last Updated")
    bc_use_default_name = fields.Boolean("Use Default Name")

    def action_create_in_bigcommerce(self):
        self.ensure_one()

        store = self.bigcommerce_store_id
        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials in the related store."))

        # Required fields validation
        missing_fields = []
        if not self.bc_currency_code:
            missing_fields.append("Currency Code")
        if not self.bc_name:
            missing_fields.append("Name")
        if not self.bc_exchange_rate:
            missing_fields.append("Currency Exchange Rate")
        if not self.bc_token_location:
            missing_fields.append("Token Location")
        if not self.bc_token:
            missing_fields.append("Token")
        if not self.bc_decimal_token:
            missing_fields.append("Decimal Token")
        if not self.bc_thousands_token:
            missing_fields.append("Thousands Token")
        if self.bc_decimal_places is None:
            missing_fields.append("Decimal Places")

        if missing_fields:
            raise UserError(_("Missing required fields:\n%s") % ", ".join(missing_fields))

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/currencies"

        payload = {
            "currency_code": self.bc_currency_code,
            "name": self.bc_name,
            "currency_exchange_rate": str(self.bc_exchange_rate),
            "token_location": self.bc_token_location,
            "token": self.bc_token,
            "decimal_token": self.bc_decimal_token,
            "thousands_token": self.bc_thousands_token,
            "decimal_places": self.bc_decimal_places,
            "enabled": self.bc_enabled,
            "is_transactional": self.bc_is_transactional,
            "is_default": self.bc_is_default,
            "auto_update": self.bc_auto_update,
            "country_iso2": self.bc_country_iso2 or "",
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 201:
            raise UserError(_("Failed to create currency in BigCommerce: %s") % response.text)

        bc_currency = response.json()

        last_updated_str = bc_currency.get('last_updated')
        if last_updated_str:
            try:
                last_updated_dt = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%SZ")
                last_updated = fields.Datetime.to_string(last_updated_dt)
            except Exception:
                last_updated = False
        else:
            last_updated = False

        self.write({
            "bc_currency_id": bc_currency.get("id"),
            "bc_currency_code": bc_currency.get("currency_code"),
            "bc_name": bc_currency.get("name"),
            "bc_enabled": bc_currency.get("enabled"),
            "bc_is_transactional": bc_currency.get("is_transactional"),
            "bc_is_default": bc_currency.get("is_default"),
            "bc_auto_update": bc_currency.get("auto_update"),
            "bc_exchange_rate": bc_currency.get("currency_exchange_rate"),
            "bc_token": bc_currency.get("token"),
            "bc_token_location": bc_currency.get("token_location"),
            "bc_decimal_places": bc_currency.get("decimal_places"),
            "bc_decimal_token": bc_currency.get("decimal_token"),
            "bc_thousands_token": bc_currency.get("thousands_token"),
            "bc_default_for_country_codes": ','.join(bc_currency.get("default_for_country_codes", [])),
            "bc_country_iso2": bc_currency.get("country_iso2"),
            "bc_last_updated": last_updated,
            "bc_use_default_name": bc_currency.get("use_default_name"),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Currency Created"),
                'type': 'success',
                'message': _("Currency '%s' successfully created in BigCommerce.") % self.bc_currency_code,
                'sticky': False,
            }
        }

    def action_delete_bigcommerce_currency(self):
        self.ensure_one()

        store = self.bigcommerce_store_id

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials in the store record."))

        if not self.bc_currency_id:
            raise UserError(_("Missing BigCommerce currency ID for this record."))

        if self.bc_is_default:
            raise UserError(_("Cannot delete the default currency from BigCommerce."))

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/currencies/{self.bc_currency_id}"

        response = requests.delete(url, headers=headers)

        if response.status_code != 204:
            raise UserError(_("Failed to delete currency: %s") % response.text)

        # Optionally delete the record locally as well
        self.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Currency Deleted"),
                'message': _("Currency successfully deleted from BigCommerce."),
                'sticky': False,
            }
        }

    def action_update_bigcommerce_currency(self):
        self.ensure_one()
        store = self.bigcommerce_store_id

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials in the store record."))

        if not self.bc_currency_id:
            raise UserError(_("Missing BigCommerce currency ID for this record."))

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/currencies/{self.bc_currency_id}"

        payload = {
            "name": self.bc_name,
            "enabled": self.bc_enabled,
            "is_transactional": self.bc_is_transactional,
            "auto_update": self.bc_auto_update,
            "currency_exchange_rate": self.bc_exchange_rate,
            "token": self.bc_token,
            "token_location": self.bc_token_location,
            "decimal_places": self.bc_decimal_places,
            "decimal_token": self.bc_decimal_token,
            "thousands_token": self.bc_thousands_token,
            "country_iso2": self.bc_country_iso2,
            "is_default": self.bc_is_default or False,
        }

        response = requests.put(url, headers=headers, json=payload)

        if response.status_code not in (200, 204):
            raise UserError(_("Failed to update currency: %s") % response.text)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Currency Updated"),
                'message': _("Currency update request sent successfully."),
                'sticky': False,
            }
        }

    def action_get_bigcommerce_currency(self):
        self.ensure_one()

        store = self.bigcommerce_store_id

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials in the store record."))

        if not self.bc_currency_id:
            raise UserError(_("Missing BigCommerce currency ID for this record."))

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/currencies/{self.bc_currency_id}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise UserError(_("Failed to fetch currency: %s") % response.text)

        currency_data = response.json()

        # Parse last_updated
        last_updated_str = currency_data.get('last_updated')
        if last_updated_str:
            try:
                last_updated_dt = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%SZ")
                last_updated = fields.Datetime.to_string(last_updated_dt)
            except Exception:
                last_updated = False
        else:
            last_updated = False

        # Update local fields
        self.write({
            "bc_currency_code": currency_data.get("currency_code"),
            "bc_name": currency_data.get("name"),
            "bc_exchange_rate": currency_data.get("currency_exchange_rate"),
            "bc_token_location": currency_data.get("token_location"),
            "bc_token": currency_data.get("token"),
            "bc_decimal_token": currency_data.get("decimal_token"),
            "bc_thousands_token": currency_data.get("thousands_token"),
            "bc_decimal_places": currency_data.get("decimal_places"),
            "bc_enabled": currency_data.get("enabled"),
            "bc_is_transactional": currency_data.get("is_transactional"),
            "bc_is_default": currency_data.get("is_default"),
            "bc_auto_update": currency_data.get("auto_update"),
            "bc_country_iso2": currency_data.get("country_iso2"),
            "bc_default_for_country_codes": ','.join(currency_data.get("default_for_country_codes", [])),
            "bc_use_default_name": currency_data.get("use_default_name"),
            "bc_last_updated": last_updated,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Currency Fetched"),
                'message': _("Currency data was successfully fetched from BigCommerce."),
                'sticky': False,
            }
        }

    def action_bulk_update_bigcommerce_currency(self):
        for currency in self:
            currency.action_update_bigcommerce_currency()

    def action_bulk_get_bigcommerce_currency(self):
        for currency in self:
            currency.action_get_bigcommerce_currency()





