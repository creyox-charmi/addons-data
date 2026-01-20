# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api,_
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)

class CrSelectStore(models.TransientModel):
    _name = 'cr.select.store'
    _description = 'Select BigCommerce Store'

    store_id = fields.Many2one('bigcommerce.store', string="BigCommerce Store", required=True)
    location_ids = fields.Many2many('stock.location', string="Locations", default=lambda self: self._default_locations())

    def _default_locations(self):
        """Set default locations from context."""
        return self.env.context.get('default_location_ids', [])

    def parse_datetime(self, dt_str):
        """Helper to parse ISO 8601 datetime to Odoo datetime."""
        if dt_str:
            dt_str = dt_str.replace('T', ' ').replace('Z', '')
            return fields.Datetime.to_datetime(dt_str)
        return False

    def action_confirm(self):
        """Process selected locations for export to BigCommerce."""
        count = 0
        self.ensure_one()
        if not self.location_ids:
            raise UserError(_("No locations selected."))

        if  len(self.location_ids) > 3:
            raise UserError(_("Maximum 3 location you can export to Bigcommerce"))

        # Example: Call a method to sync locations with BigCommerce
        for location in self.location_ids:
            location.action_export_to_bigcommerce(self.store_id)
            count += 1

        url = f"https://api.bigcommerce.com/stores/{self.store_id.store_hash}/v3/inventory/locations"
        headers = {
            "X-Auth-Token": self.store_id.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise UserError(_("Failed to fetch inventory locations: %s") % response.text)

        data = response.json().get('data', [])
        created_count = 0

        InventoryLocation = self.env['stock.location']
        for location in data:
            address = location.get('address', {})
            geo = address.get('geo_coordinates', {})
            existing = InventoryLocation.search([
                ('complete_name', '=', location.get('label')),
                ('bigcommerce_store_id', '=', self.store_id.id),
            ], limit=1)

            vals = {
                'bigcommerce_store_id': self.store_id.id,
                'bc_location_id': location['id'],
                'code': location.get('code'),
                'label': location.get('label'),
                'description': location.get('description'),
                'managed_by_external_source': location.get('managed_by_external_source'),
                'type_id': location.get('type_id'),
                'enabled': location.get('enabled'),
                'operating_hours': location.get('operating_hours'),
                'time_zone': location.get('time_zone'),
                'created_at': self.parse_datetime(location.get('created_at')),
                'updated_at': self.parse_datetime(location.get('updated_at')),
                'address1': address.get('address1'),
                'address2': address.get('address2'),
                'city': address.get('city'),
                'state': address.get('state'),
                'zip': address.get('zip'),
                'phone': address.get('phone'),
                'country_code': address.get('country_code'),
                'latitude': geo.get('latitude'),
                'longitude': geo.get('longitude'),
                'storefront_visibility': location.get('storefront_visibility'),
            }

            if existing:
                existing.write(vals)

        self.env['cr.data.processing.log']._log_data_processing(
            cr_shop_id=self.store_id.id,
            record_count=count,
            cr_message="Successfully Export Locations",
            status='success',
            timespan=str(fields.Datetime.now()),
            initiated_at=str(fields.Datetime.now()),
            error_message='',
            cr_user_id=self.env.uid
        )

