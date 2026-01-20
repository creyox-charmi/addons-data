from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
from datetime import datetime

class BigCommerceCurrency(models.Model):
    _name = 'bigcommerce.currency'
    _description = 'BigCommerce Currency'
    _rec_name = 'currency_code'
    _order = 'is_default desc, currency_code'

    store_id = fields.Many2one('bigcommerce.store', string="Store", required=True, ondelete='cascade')
    bigcommerce_currency_id = fields.Integer("BigCommerce Currency ID", readonly=True)
    currency_code = fields.Char("Currency Code", required=True)
    name = fields.Char("Name")
    enabled = fields.Boolean("Enabled")
    is_transactional = fields.Boolean("Transactional")
    is_default = fields.Boolean("Default Currency")
    auto_update = fields.Boolean("Auto Update")
    currency_exchange_rate = fields.Float("Exchange Rate")
    token = fields.Char("Token")
    token_location = fields.Selection([('left', 'Left'), ('right', 'Right')], string="Token Location")
    decimal_places = fields.Integer("Decimal Places")
    decimal_token = fields.Char("Decimal Token")
    thousands_token = fields.Char("Thousands Token")
    default_for_country_codes = fields.Char("Default For Countries")
    country_iso2 = fields.Char("Country ISO2")
    last_updated = fields.Datetime("Last Updated")
    use_default_name = fields.Boolean("Use Default Name")

    _sql_constraints = [
        ('unique_currency_per_store', 'unique(store_id, currency_code)',
         'Currency must be unique per store.')
    ]

    # def action_create_in_bigcommerce(self):
    #     self.ensure_one()
    #
    #     store = self.store_id
    #     if not store.access_token or not store.store_hash:
    #         raise UserError(_("Missing API credentials in the related store."))
    #
    #     # Required fields validation
    #     missing_fields = []
    #     if not self.currency_code:
    #         missing_fields.append("Currency Code")
    #     if not self.name:
    #         missing_fields.append("Name")
    #     if not self.currency_exchange_rate:
    #         missing_fields.append("Currency Exchange Rate")
    #     if not self.token_location:
    #         missing_fields.append("Token Location")
    #     if not self.token:
    #         missing_fields.append("Token")
    #     if not self.decimal_token:
    #         missing_fields.append("Decimal Token")
    #     if not self.thousands_token:
    #         missing_fields.append("Thousands Token")
    #     if self.decimal_places is None:
    #         missing_fields.append("Decimal Places")
    #
    #     if missing_fields:
    #         raise UserError(_("Missing required fields:\n%s") % ", ".join(missing_fields))
    #
    #     headers = {
    #         "X-Auth-Token": store.access_token,
    #         "Accept": "application/json",
    #         "Content-Type": "application/json",
    #     }
    #
    #     url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/currencies"
    #
    #     payload = {
    #         "currency_code": self.currency_code,
    #         "name": self.name,
    #         "currency_exchange_rate": str(self.currency_exchange_rate),
    #         "token_location": self.token_location,
    #         "token": self.token,
    #         "decimal_token": self.decimal_token,
    #         "thousands_token": self.thousands_token,
    #         "decimal_places": self.decimal_places,
    #         "enabled": self.enabled,
    #         "is_transactional": self.is_transactional,
    #         "is_default": self.is_default,
    #         "auto_update": self.auto_update,
    #         "country_iso2": self.country_iso2 or "",
    #     }
    #
    #     response = requests.post(url, headers=headers, json=payload)
    #
    #     if response.status_code != 201:
    #         raise UserError(_("Failed to create currency in BigCommerce: %s") % response.text)
    #
    #     bc_currency = response.json()
    #
    #     # from datetime import datetime
    #     # last_updated = bc_currency.get("last_updated")
    #     # if last_updated:
    #     #     last_updated = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%SZ")
    #
    #     last_updated_str = bc_currency.get('last_updated')
    #     if last_updated_str:
    #         try:
    #             last_updated_dt = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%SZ")
    #             last_updated = fields.Datetime.to_string(last_updated_dt)
    #         except Exception:
    #             last_updated = False
    #     else:
    #         last_updated = False
    #
    #     self.write({
    #         "bigcommerce_currency_id": bc_currency.get("id"),
    #         "currency_code": bc_currency.get("currency_code"),
    #         "name": bc_currency.get("name"),
    #         "enabled": bc_currency.get("enabled"),
    #         "is_transactional": bc_currency.get("is_transactional"),
    #         "is_default": bc_currency.get("is_default"),
    #         "auto_update": bc_currency.get("auto_update"),
    #         "currency_exchange_rate": bc_currency.get("currency_exchange_rate"),
    #         "token": bc_currency.get("token"),
    #         "token_location": bc_currency.get("token_location"),
    #         "decimal_places": bc_currency.get("decimal_places"),
    #         "decimal_token": bc_currency.get("decimal_token"),
    #         "thousands_token": bc_currency.get("thousands_token"),
    #         "default_for_country_codes": ','.join(bc_currency.get("default_for_country_codes", [])),
    #         "country_iso2": bc_currency.get("country_iso2"),
    #         "last_updated": last_updated,
    #         "use_default_name": bc_currency.get("use_default_name"),
    #     })
    #
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _("Currency Created"),
    #             'type': 'success',
    #             'message': _("Currency '%s' successfully created in BigCommerce.") % self.currency_code,
    #             'sticky': False,
    #         }
    #     }

    def action_update_bigcommerce_currency(self):
        self.ensure_one()
        store = self.store_id

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials in the store record."))

        if not self.bigcommerce_currency_id:
            raise UserError(_("Missing BigCommerce currency ID for this record."))

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/currencies/{self.bigcommerce_currency_id}"

        payload = {
            "name": self.name,
            "enabled": self.enabled,
            "is_transactional": self.is_transactional,
            "auto_update": self.auto_update,
            "currency_exchange_rate": self.currency_exchange_rate,
            "token": self.token,
            "token_location": self.token_location,
            "decimal_places": self.decimal_places,
            "decimal_token": self.decimal_token,
            "thousands_token": self.thousands_token,
            "country_iso2": self.country_iso2,
            "is_default": self.is_default if self.is_default else False
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

    def action_delete_bigcommerce_currency(self):
        self.ensure_one()

        store = self.store_id

        if not store.access_token or not store.store_hash:
            raise UserError(_("Missing API credentials in the store record."))

        if not self.bigcommerce_currency_id:
            raise UserError(_("Missing BigCommerce currency ID for this record."))

        if self.is_default:
            raise UserError(_("Cannot delete the default currency from BigCommerce."))

        headers = {
            "X-Auth-Token": store.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"https://api.bigcommerce.com/stores/{store.store_hash}/v2/currencies/{self.bigcommerce_currency_id}"

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


    def action_delete_all_bigcommerce_currencies(self):
        self.ensure_one()
        if not self.access_token or not self.store_hash:
            raise UserError(_("Missing API credentials."))

        url = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2/currencies"
        headers = {
            "X-Auth-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204 or response.status_code == 200:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Currencies Deleted"),
                    'message': _("All non-default currencies were successfully deleted."),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("Failed to delete currencies: %s") % response.text)

