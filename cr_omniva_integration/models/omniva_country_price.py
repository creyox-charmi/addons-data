# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OmnivaCountryPrice(models.Model):
    _name = "omniva.country.price"
    _description = "Omniva Country-Based Pricing"
    _order = "company_id, delivery_channel, country_id"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
    )
    delivery_channel = fields.Selection(
        [
            ("COURIER", "Courier"),
            ("PARCEL_MACHINE", "Parcel Machine"),
            ("POST_OFFICE", "Post Office"),
        ],
        string="Delivery Channel",
        required=True,
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        required=True,
        domain=[("code", "in", ["EE", "FI", "LV", "LT", "IN"])],
    )
    price = fields.Float(string="Price", required=True, digits="Product Price")

    _sql_constraints = [
        (
            "unique_company_channel_country",
            "unique(company_id, delivery_channel, country_id)",
            "A price already exists for this combination of Company, Delivery Channel, and Country!",
        )
    ]

    @api.constrains("price")
    def _check_price(self):
        for record in self:
            if record.price < 0:
                raise ValidationError(_("Price must be positive"))

    @api.model_create_multi
    def create(self, vals_list):
        records = super(OmnivaCountryPrice, self).create(vals_list)

        for record in records:
            carriers = self.env["delivery.carrier"].search(
                [("delivery_type", "=", "omniva")]
            )

            for carrier in carriers:
                if record.country_id not in carrier.country_ids:
                    carrier.write({"country_ids": [(4, record.country_id.id)]})

        return records

    def write(self, vals):
        result = super(OmnivaCountryPrice, self).write(vals)
        if "country_id" in vals:
            for record in self:
                carriers = self.env["delivery.carrier"].search(
                    [("delivery_type", "=", "omniva")]
                )

                for carrier in carriers:
                    if record.country_id not in carrier.country_ids:
                        carrier.write({"country_ids": [(4, record.country_id.id)]})

        return result

    def unlink(self):
        countries_to_check = {}

        for record in self:
            key = (record.company_id.id, record.country_id.id)
            countries_to_check[key] = record

        result = super(OmnivaCountryPrice, self).unlink()

        for (company_id, country_id), record in countries_to_check.items():
            other_records = self.search(
                [("company_id", "=", company_id), ("country_id", "=", country_id)],
                limit=1,
            )

            if not other_records:
                carriers = self.env["delivery.carrier"].search(
                    [("delivery_type", "=", "omniva")]
                )

                for carrier in carriers:
                    carrier.write({"country_ids": [(3, country_id)]})

        return result

    @api.onchange("country_id")
    def _onchange_country_id(self):
        """Sync carrier country_ids with available price records"""
        if self.country_id:
            # Get all countries from all price records
            all_price_records = self.search([])
            available_country_ids = set()

            for record in all_price_records:
                if record.id != self._origin.id:  # Exclude current record if editing
                    available_country_ids.add(record.country_id.id)

            # Add the new country being set
            available_country_ids.add(self.country_id.id)

            # Update all omniva carriers
            carriers = self.env["delivery.carrier"].search(
                [("delivery_type", "=", "omniva")]
            )

            for carrier in carriers:
                carrier.write({"country_ids": [(6, 0, list(available_country_ids))]})
