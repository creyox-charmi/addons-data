# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cr_cost_total = fields.Char(
        string="Cost(Included Overhead)", compute="_compute_cost_total"
    )

    @api.depends("standard_price")
    def _compute_cost_total(self):
        price = 0
        for d in self.bom_ids.cr_overhead_data_ids:
            price = price + d.cost

        self.cr_cost_total = self.standard_price + price
