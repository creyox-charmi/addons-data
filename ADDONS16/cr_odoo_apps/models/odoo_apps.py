# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class OdooApps(models.Model):
    _name = "cr.odoo.apps"
    _description = "Odoo Apps"

    name = fields.Char(string="Name")
    tech_name = fields.Char(string="Technical Name")
    version_ids = fields.Many2many("cr.versions.odoo", string="Available Versions")
    category_id = fields.Many2one("cr.categories", string="Category")
    active = fields.Boolean(default=True)
    non_migrated_version_ids = fields.Many2many(
        "cr.versions.odoo",
        "version_app_relation",
        "app_id",
        "version_id",
        string="Non Migrated Versions",
    )

    def name_get(self):
        result = []
        for record in self:
            display_name = record.tech_name or record.name
            result.append((record.id, display_name))
        return result

    @api.constrains("tech_name")
    def _check_unique_tech_name(self):
        for record in self:
            # Search for records with the same tech_name
            existing_records = self.search(
                [("tech_name", "=", record.tech_name), ("id", "!=", record.id)]
            )
            if existing_records:
                raise ValidationError(
                    f'The Technical Name "{record.tech_name}" must be unique.'
                )
