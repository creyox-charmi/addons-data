# -*- coding: utf-8 -*-
"""SmartPosti Pickup Places Management"""

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SmartPostiPlace(models.Model):
    _name = "smartposti.place"
    _description = "SmartPosti Pickup Places"
    _order = "country, city, name"
    _rec_name = "display_name"

    place_id = fields.Char(
        string="Place ID",
        required=True,
        index=True,
        help="Unique place identifier from SmartPosti",
    )
    name = fields.Char(string="Name", required=True, index=True)
    city = fields.Char(string="City", required=True, index=True)
    address = fields.Char(string="Address", required=True)
    country = fields.Selection(
        [("EE", "Estonia"), ("FI", "Finland"), ("LV", "Latvia"), ("LT", "Lithuania")],
        string="Country",
        required=True,
        index=True,
    )
    postal_code = fields.Char(string="Postal Code", index=True)
    routing_code = fields.Char(string="Routing Code")
    availability = fields.Char(string="Availability")
    description = fields.Text(string="Description")
    place_type = fields.Selection(
        [
            ("apt", "Blue Box (APT)"),
            ("ipb", "White Box (IPB)"),
            ("po", "Post Office"),
            ("pudo", "Parcel Point"),
        ],
        string="Type",
        required=True,
        index=True,
    )
    latitude = fields.Float(string="Latitude", digits=(10, 6))
    longitude = fields.Float(string="Longitude", digits=(10, 6))
    group_id = fields.Integer(string="Group ID")
    group_name = fields.Char(string="Group Name")
    group_sort = fields.Integer(string="Group Sort")
    is_outdoor = fields.Boolean(string="Outdoor Location")
    is_express = fields.Boolean(string="Express Available")
    created_date = fields.Datetime(string="Created Date", readonly=True)
    updated_date = fields.Datetime(string="Updated Date", readonly=True)
    active = fields.Boolean(string="Active", default=True)
    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )

    _sql_constraints = [
        ("unique_place_id", "unique(place_id)", "Place ID must be unique!")
    ]

    @api.depends("name", "city", "address", "place_type")
    def _compute_display_name(self):
        """Generate user-friendly display name"""
        type_dict = dict(self._fields["place_type"].selection)
        for place in self:
            place.display_name = f"{place.name} - {place.city} ({type_dict.get(place.place_type, place.place_type)})"

    @staticmethod
    def _safe_float(value, default=0.0):
        """Safely convert value to float

        Args:
            value: Value to convert
            default: Default if conversion fails

        Returns:
            float: Converted value or default
        """
        try:
            if value in ("", None):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_int(value, default=0):
        """Safely convert value to integer"""
        try:
            if value in ("", None):
                return default
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_bool(value):
        """Safely convert value to boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return False

    def _prepare_place_values(self, place_data, country_code):
        """Prepare place values from API data

        Args:
            place_data: Place data dict from API
            country_code: Country code

        Returns:
            dict: Values for create/write
        """
        values = {
            "place_id": place_data.get("place_id"),
            "name": place_data.get("name") or "Unknown",
            "city": place_data.get("city") or "Unknown",
            "address": place_data.get("address") or "",
            "country": (place_data.get("country") or country_code).upper(),
            "postal_code": place_data.get("postalcode") or "",
            "routing_code": place_data.get("routingcode") or "",
            "availability": place_data.get("availability") or "",
            "description": place_data.get("description") or "",
            "place_type": (place_data.get("type") or "apt").lower(),
            "latitude": self._safe_float(place_data.get("lat")),
            "longitude": self._safe_float(place_data.get("lng")),
            "group_id": self._safe_int(place_data.get("group_id")),
            "group_name": place_data.get("group_name") or "",
            "group_sort": self._safe_int(place_data.get("group_sort")),
            "is_outdoor": self._safe_bool(place_data.get("is_outdoor")),
            "is_express": self._safe_bool(place_data.get("is_express")),
            "active": True,
        }

        # Parse dates safely
        for date_field in ("created_date", "updated_date"):
            if place_data.get(date_field):
                try:
                    values[date_field] = fields.Datetime.to_datetime(
                        place_data[date_field]
                    )
                except Exception as e:
                    _logger.warning(f"Failed to parse {date_field}: {e}")

        return values

    @api.model
    def sync_places_for_country(self, country_code, carrier=None):
        """Synchronize places from SmartPosti API

        Args:
            country_code: Country code (EE, FI, LV, LT)
            carrier: delivery.carrier record (optional)

        Returns:
            dict: Sync statistics
        """
        # Find carrier if not provided
        if not carrier:
            carrier = self.env["delivery.carrier"].search(
                [
                    ("delivery_type", "=", "smartposti"),
                    ("smartposti_country", "=", country_code),
                ],
                limit=1,
            )

            if not carrier:
                carrier = self.env["delivery.carrier"].search(
                    [("delivery_type", "=", "smartposti")], limit=1
                )

        if not carrier:
            raise UserError(_("No SmartPosti carrier configured"))

        try:
            # Fetch places from API
            client = carrier._get_smartposti_client()
            places_data = client.get_places(country_code)

            if places_data.get("error"):
                raise UserError(_("API Error: %s") % places_data["error"])

            # Extract places list
            places_list = places_data.get("places", {}).get("item", [])
            if not isinstance(places_list, list):
                places_list = [places_list] if places_list else []

            created_count = updated_count = skipped_count = 0

            # Process each place
            for place_data in places_list:
                place_id = place_data.get("place_id")

                # Generate random place_id if missing or empty
                if not place_id or place_id == "":
                    import uuid

                    place_id = f"SP_{country_code}_{uuid.uuid4().hex[:12].upper()}"
                    place_data["place_id"] = place_id
                    _logger.warning(
                        f'Generated random place_id for place: {place_data.get("name", "Unknown")} - {place_id}'
                    )

                try:
                    existing_place = self.search([("place_id", "=", place_id)], limit=1)
                    values = self._prepare_place_values(place_data, country_code)

                    if existing_place:
                        existing_place.write(values)
                        updated_count += 1
                    else:
                        self.create(values)
                        created_count += 1

                except Exception as e:
                    _logger.error(f"Failed to process place {place_id}: {str(e)}")
                    skipped_count += 1
                    continue

            _logger.info(
                f"Places sync for {country_code}: "
                f"{created_count} created, {updated_count} updated, {skipped_count} skipped"
            )

            return {
                "created": created_count,
                "updated": updated_count,
                "skipped": skipped_count,
                "total": len(places_list),
            }

        except Exception as e:
            _logger.error(f"Places sync failed for {country_code}: {str(e)}")
            raise UserError(_("Failed to sync places: %s") % str(e))
