# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, api

class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):

        filtered_procurements = []

        for procurement, rule in procurements:
            product = procurement.product_id
            values = procurement.values

            bom_id = values.get("bom_id")
            bom_line_id = values.get("bom_line_id")
            related_mo_id = self.env['mrp.production'].browse(int(values.get("production_id"))).id

            skip_procurement = False

            if bom_id and bom_line_id:
                # Check if active session context has po_created=True
                active_ctx = self.env["mrp.bom.context"].search([
                    ("root_bom_id", "=", bom_id),
                    ("bom_line_id", "=", bom_line_id),
                    ("related_mo_id", "=", related_mo_id)
                ])


                if active_ctx and active_ctx.po_created:
                    skip_procurement = True


            if skip_procurement:
                continue

            filtered_procurements.append((procurement, rule))

        if filtered_procurements:
            return super()._run_buy(filtered_procurements)

        return True


