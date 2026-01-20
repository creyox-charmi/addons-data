# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _


class Manufacturing(models.Model):
    _inherit = "mrp.production"

    purchase_count = fields.Integer(compute="_purchase_order_count")
    delivery_count = fields.Integer(compute="_delivery_count")
    receipt_count = fields.Integer(compute="_receipt_count")

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

    def _purchase_order_count(self):
        for order in self:
            purchase = self.env["purchase.order"].search_count(
                [("origin", "=", self.name)]
            )
            order.purchase_count = purchase

    def _delivery_count(self):
        self.delivery_count = 0
        for order in self:
            delivery = self.env["stock.picking"].search_count(
                [
                    ("mrp_id", "=", self.id),
                    ("picking_type_code", "=", "outgoing"),
                ]
            )
            order.delivery_count = delivery

    def _receipt_count(self):
        self.receipt_count = 0
        for order in self:
            receipt = self.env["stock.picking"].search_count(
                [
                    ("mrp_id", "=", self.id),
                    ("picking_type_code", "=", "incoming"),
                ]
            )
            order.receipt_count = receipt

    def view_subcontract_purchase(self):
        po_list = []
        purchase_ids = self.env["purchase.order"].search(
            [("origin", "=", self.name)]
        )
        if purchase_ids:
            for purchase_id in purchase_ids:
                po_list.append(purchase_id.id)

        return {
            "name": _("Subcontract Purchase"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "purchase.order",
            "domain": [("id", "in", po_list)],
        }

    def view_subcontract_delivery(self):
        delivery_list = []
        delivery_ids = self.env["stock.picking"].search(
            [("mrp_id", "=", self.id), ("picking_type_code", "=", "outgoing")]
        )
        if delivery_ids:
            for delivery_id in delivery_ids:
                delivery_list.append(delivery_id.id)

        return {
            "name": _("Subcontract Delivery"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "stock.picking",
            "domain": [("id", "in", delivery_list)],
        }

    def view_subcontract_receipt(self):
        receipt_list = []
        receipt_ids = self.env["stock.picking"].search(
            [("mrp_id", "=", self.id), ("picking_type_code", "=", "incoming")]
        )
        if receipt_ids:
            for receipt_id in receipt_ids:
                receipt_list.append(receipt_id.id)

        return {
            "name": _("Subcontract Receipt"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "stock.picking",
            "domain": [("id", "in", receipt_list)],
        }

