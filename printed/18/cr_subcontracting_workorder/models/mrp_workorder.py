# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class workOrder(models.Model):
    _inherit = "mrp.workorder"

    is_subcontract_wo = fields.Boolean(compute="_subcontract_workorder")
    got_subcontracted_product = fields.Boolean(compute="_compute_receipt_done")
    purchase_count = fields.Integer(compute="_purchase_order_count")
    delivery_count = fields.Integer(compute="_delivery_count")
    receipt_count = fields.Integer(compute="_receipt_count")
    is_return_subcontracted_product = fields.Boolean(compute="_compute_receipt_done")
    bom_id = fields.Many2one(related="operation_id.bom_id", string="Bill Of Material")

    @api.depends("receipt_count")
    def _compute_receipt_done(self):
        for order in self:
            receipt_id = self.env["stock.picking"].search(
                [
                    ("workorder_id", "=", order.id),
                    ("picking_type_code", "=", "incoming"),
                    ("state", "=", "done"),
                ]
            )
            if receipt_id:
                order.is_return_subcontracted_product = True
            else:
                order.is_return_subcontracted_product = False

    def _purchase_order_count(self):
        for order in self:
            purchase = self.env["purchase.order"].search_count(
                [("workorder_id", "=", order.id)]
            )
            order.purchase_count = purchase

    def _delivery_count(self):
        for order in self:
            delivery = self.env["stock.picking"].search_count(
                [
                    ("workorder_id", "=", order.id),
                    ("picking_type_code", "=", "outgoing"),
                ]
            )
            order.delivery_count = delivery

    def _receipt_count(self):
        for order in self:
            receipt = self.env["stock.picking"].search_count(
                [
                    ("workorder_id", "=", order.id),
                    ("picking_type_code", "=", "incoming"),
                ]
            )
            order.receipt_count = receipt

    def view_subcontract_purchase(self):
        po_list = []
        purchase_ids = self.env["purchase.order"].search(
            [("workorder_id", "=", self.id)]
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
            [("workorder_id", "=", self.id), ("picking_type_code", "=", "outgoing")]
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
            [("workorder_id", "=", self.id), ("picking_type_code", "=", "incoming")]
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

    @api.depends("operation_id")
    def _subcontract_workorder(self):
        print("YESSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
        for subcontract in self:
            if (
                subcontract.name == subcontract.operation_id.name
                and subcontract.operation_id.is_subcontract
                and subcontract.operation_id.is_show_wo_subcontract
            ):
                subcontract.is_subcontract_wo = True
            else:
                subcontract.is_subcontract_wo = False

    def button_start_subcontract(self):
        print("button_start_subcontract")
        po = self.subcontract_purchase()
        self.subcontract_delivery(po)

    def subcontract_purchase(self):
        po_line_lst = []
        for order in self:
            order.button_start()
            if order.production_id.state != "progress":
                order.production_id.write({"state": "progress"})
            purchase_dict = {
                "partner_id": order.operation_id.partner_id.id,
                "workorder_id": order.id,
                "mrp_id": order.production_id.id,
                "origin":order.production_id.name
            }
            purchase_id = self.env["purchase.order"].create(purchase_dict)

            if order.operation_id.purchase_description:
                description = order.production_id.name + " " + order.operation_id.service_product_id.name + " " + order.operation_id.purchase_description
            else:
                description = order.production_id.name + " " + order.operation_id.service_product_id.name
            print(order.operation_id.cost_per_unit)
            print(order.operation_id.minimum_order_amount)
            print("pp : ",max(order.operation_id.cost_per_unit, order.operation_id.minimum_order_amount))
            po_line_lst.append(
                (
                    0,
                    0,
                    {
                        "product_id": order.operation_id.service_product_id.id,
                        "name": order.operation_id.service_product_id.name + description,
                        "date_planned": datetime.now(),
                        "product_qty": order.production_id.product_qty,
                        "product_uom": order.operation_id.service_product_id.uom_id.id,
                        "price_unit": max(order.operation_id.cost_per_unit, order.operation_id.minimum_order_amount),
                    },
                )
            )
            if purchase_id:
                purchase_id.order_line = po_line_lst
            print("purchase_id.name  : ",purchase_id.name)
            return purchase_id.name

    def subcontract_delivery(self,po):
        delivery_line_lst = []
        for order in self:
            picking_type_id = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "outgoing"),
                    (
                        "warehouse_id",
                        "=",
                        order.production_id.picking_type_id.warehouse_id.id,
                    ),
                ],
                limit=1,
            )

            description = order.production_id.name + " " + order.production_id.product_id.name
            if picking_type_id:
                delivery_dict = {
                    "partner_id": order.operation_id.partner_id.id,
                    "picking_type_id": picking_type_id.id,
                    # "location_id": picking_type_id.default_location_src_id.id,
                    "location_id": order.production_id.location_dest_id.id,
                    "location_dest_id": order.operation_id.partner_id.property_stock_customer.id,
                    "workorder_id": order.id,
                    "mrp_id": order.production_id.id,
                    "origin": po
                }
                delivery_id = self.env["stock.picking"].create(delivery_dict)

                delivery_line_lst.append(
                    (
                        0,
                        0,
                        {
                            "product_id": order.production_id.product_id.id,
                            "name": description,
                            "product_uom": order.production_id.product_id.uom_id.id,
                            "product_uom_qty": order.production_id.product_qty,
                            # "location_id": picking_type_id.default_location_src_id.id,
                            "location_id": order.production_id.location_dest_id.id,
                            "location_dest_id": order.operation_id.partner_id.property_stock_customer.id,
                        },
                    )
                )
                if delivery_id:
                    delivery_id.move_ids_without_package = delivery_line_lst

    def button_done_subcontract(self):
        for order in self:
            order.button_finish()
            # order.record_production()
