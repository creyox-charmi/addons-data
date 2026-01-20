# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Manufacturing(models.Model):
    _inherit = "mrp.production"

    def action_cancel(self):
        mrp_cancel = super(Manufacturing, self).action_cancel()
        if mrp_cancel:
            po_cancel = self.env["purchase.order"].search([("mrp_id", "=", self.id)])
            stock_cancel = self.env["stock.picking"].search([("mrp_id", "=", self.id)])
            for rec in po_cancel:
                rec.button_cancel()
            for rec in stock_cancel:
                rec.action_cancel()
        return mrp_cancel
