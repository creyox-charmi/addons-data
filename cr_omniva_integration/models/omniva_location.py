# -*- coding: utf-8 -*-

import logging
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OmnivaLocation(models.Model):
    _name = "omniva.location"
    _description = "Omniva Pickup Locations"
    _order = "country, city, name"
    _rec_name = "display_name"

    # Fields from JSON
    zip_code = fields.Char("ZIP", index=True)
    name = fields.Char("Name", required=True, index=True)
    location_type = fields.Selection(
        [("0", "Parcel Machine"), ("1", "Post Office / Pickup Point")],
        string="Type",
        required=True,
        index=True,
    )
    country = fields.Selection(
        [("EE", "Estonia"), ("LV", "Latvia"), ("LT", "Lithuania"), ("FI", "Finland")],
        string="Country",
        required=True,
        index=True,
    )
    city = fields.Char("City", index=True)
    address = fields.Char("Address")
    latitude = fields.Float("Latitude", digits=(10, 6))
    longitude = fields.Float("Longitude", digits=(10, 6))
    comment_est = fields.Text("Comment (EST)")
    comment_eng = fields.Text("Comment (ENG)")
    comment_rus = fields.Text("Comment (RUS)")
    comment_lat = fields.Text("Comment (LAT)")
    comment_lit = fields.Text("Comment (LIT)")
    active = fields.Boolean("Active", default=True)

    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )

    _sql_constraints = [
        (
            "unique_zip_name",
            "unique(zip_code, name, country)",
            "Location must be unique!",
        )
    ]

    @api.depends("name", "city", "location_type")
    def _compute_display_name(self):
        """Generate display name"""
        type_dict = dict(self._fields["location_type"].selection)
        for location in self:
            location_type = type_dict.get(location.location_type, "")
            location.display_name = (
                f"{location.name} - {location.city} ({location_type})"
            )

    @api.model
    def sync_locations_from_omniva(self, country=None):
        """Sync locations from Omniva JSON API"""

        # Use full locations list (includes Finland)
        url = "https://www.omniva.ee/locationsfull.json"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            created = updated = skipped = 0

            for item in data:
                # Filter by country if specified
                if country and item.get("A0_NAME") != country:
                    continue

                try:
                    values = {
                        "zip_code": item.get("ZIP"),
                        "name": item.get("NAME"),
                        "location_type": item.get("TYPE", "0"),
                        "country": item.get("A0_NAME"),
                        "city": item.get("A2_NAME") or item.get("A1_NAME"),
                        "address": item.get("A5_NAME") or item.get("A7_NAME"),
                        "latitude": float(item.get("Y_COORDINATE", 0)),
                        "longitude": float(item.get("X_COORDINATE", 0)),
                        "comment_est": item.get("comment_est"),
                        "comment_eng": item.get("comment_eng"),
                        "comment_rus": item.get("comment_rus"),
                        "comment_lat": item.get("comment_lat"),
                        "comment_lit": item.get("comment_lit"),
                        "active": True,
                    }

                    # Find existing
                    existing = self.search(
                        [
                            ("zip_code", "=", values["zip_code"]),
                            ("name", "=", values["name"]),
                            ("country", "=", values["country"]),
                        ],
                        limit=1,
                    )

                    if existing:
                        existing.write(values)
                        updated += 1
                    else:
                        self.create(values)
                        created += 1

                except Exception as e:
                    _logger.error(f"Failed to process location: {e}")
                    skipped += 1

            _logger.info(
                f"Omniva sync: {created} created, {updated} updated, {skipped} skipped"
            )

            return {
                "created": created,
                "updated": updated,
                "skipped": skipped,
                "total": len(data),
            }

        except Exception as e:
            raise UserError(_("Failed to sync Omniva locations: %s") % str(e))
