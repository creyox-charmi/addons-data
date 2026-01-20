# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    cfe_project_location_id = fields.Many2one(
        'stock.location',
        string='Project location',
        domain=[('usage', '=', 'internal')],
        help='Destination location for Customer Furnished Equipment'
    )
    production_id = fields.Many2one(
        'mrp.production',
        string="Manufacturing Order",
        help="Custom link between PO and MO"
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        string="MRP BOM",
    )

    def _prepare_picking(self):
        """Override to set destination location from BOM if available."""
        res = super()._prepare_picking()
        # Check if PO is linked to a BOM via mo_internal_ref
        if self.cfe_project_location_id:
            res["location_dest_id"] = self.cfe_project_location_id.id
        return res


    def button_confirm(self):
        res = super().button_confirm()

        for order in self:
            if order.cfe_project_location_id:
                pickings = order.picking_ids.filtered(lambda p: p.state in ['draft', 'waiting', 'confirmed'])
                for picking in pickings:
                    _logger.info(
                        "🔄 Updating picking %s destination to CFE location %s (%s)",
                        picking.name, order.cfe_project_location_id.display_name, order.cfe_project_location_id.id
                    )
                    picking.location_dest_id = order.cfe_project_location_id.id
                    picking.move_ids.location_dest_id = order.cfe_project_location_id.id

        return res



