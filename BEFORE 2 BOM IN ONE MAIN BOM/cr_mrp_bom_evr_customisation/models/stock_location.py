# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import api, fields, models

class StockLocation(models.Model):
    _inherit = "stock.location"

    location_category = fields.Selection(
        [("free", "Free Location"), ("project", "Project Location")],
        string="Location Category",
    )

    @api.onchange("location_id")
    def _onchange_location_id(self):
        """Set default category from parent if empty."""
        if not self.location_category and self.location_id.location_category:
            self.location_category = self.location_id.location_category

    @api.model
    def create(self, vals):
        if not vals.get("location_category") and vals.get("location_id"):
            parent = self.browse(vals["location_id"])
            vals["location_category"] = parent.location_category
        return super().create(vals)

    def write(self, vals):
        if "location_id" in vals and not vals.get("location_category"):
            parent = self.browse(vals["location_id"])
            vals["location_category"] = parent.location_category
        res = super().write(vals)
        if 'location_category' in vals:
            # Trigger recompute for all BOM lines when location category changes
            bom_lines = self.env['mrp.bom.line'].search([])
            if bom_lines:
                bom_lines._compute_free_to_use()
        return res
