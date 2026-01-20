# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class FiscalPositionPostalCode(models.Model):
    _name = "account.fiscal.position.postal"
    _description = "Fiscal Position Postal Code"
    _rec_name = "display_name"

    country_id = fields.Many2one("res.country", string="Country", required=True)
    postal_code = fields.Char("Postal Code", required=True)
    fiscal_position_id = fields.Many2one("account.fiscal.position", string="Fiscal Position", ondelete="cascade", required=True)

    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends("country_id", "postal_code")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.country_id.code or ''} - {rec.postal_code}"
