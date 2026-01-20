# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api, _

class Stock(models.Model):
    _inherit = "stock.picking"

    workorder_id = fields.Many2one("mrp.workorder", string="Work Order")
    mrp_id = fields.Many2one("mrp.production", string="Manufacturing")
    temp_quantity = fields.Boolean(string='temp_quantity',default=False)

    def _return_subcontracting_picking(self,po):
        receipt_line_dict = []
        picking_type_id = self.env["stock.picking.type"].search(
            [
                ("code", "=", "incoming"),
                ("warehouse_id", "=", self.mrp_id.picking_type_id.warehouse_id.id),
            ],
            limit=1,
        )
        for picking in self:
            if picking.workorder_id and picking.mrp_id:
                receipt_dict = {
                    "partner_id": picking.workorder_id.operation_id.partner_id.id,
                    "picking_type_id": picking_type_id.id,
                    "location_id": picking_type_id.default_location_src_id.id,
                    "location_dest_id": picking.mrp_id.location_dest_id.id,
                    "workorder_id": picking.workorder_id.id,
                    "mrp_id": picking.mrp_id.id,
                    "origin": po
                }
                description = picking.mrp_id.name + " " + picking.mrp_id.product_id.name
                receipt_id = self.env["stock.picking"].create(receipt_dict)
                for qty in picking.move_line_ids_without_package:
                    product_uom_qty_done = qty.quantity
                    break
                receipt_line_dict.append(
                    (
                        0,
                        0,
                        {
                            "product_id": picking.mrp_id.product_id.id,
                            "name": description,
                            "product_uom": picking.mrp_id.product_id.uom_id.id,
                            "product_uom_qty": product_uom_qty_done,
                            "location_id": picking_type_id.default_location_src_id.id,
                            "location_dest_id": picking.mrp_id.location_dest_id.id,
                        },
                    )
                )
                if receipt_id:
                    receipt_id.move_ids_without_package = receipt_line_dict

    def _action_done(self):
        print("done")
        super_picking = super(Stock, self)._action_done()
        for rec in self:
            if rec.picking_type_id and rec.picking_type_id.code == "outgoing":
                rec._return_subcontracting_picking(rec.origin)
        return super_picking

    def action_confirm(self):
        print("confirm")
        for move in self.move_ids_without_package:
            if move.product_id:
                if move.product_uom_qty:
                    move.quantity = move.product_uom_qty
        res = super(Stock, self).action_confirm()

    def button_validate(self):
        self._set_auto_lot()
        res = super(Stock, self).button_validate()
        print("zzzzzzzzzzzzzzzzzzzzz")
        print("self.move_line_ids : ",self.move_line_ids)
        lines = self.move_line_ids
        code = self.picking_type_id.code
        print("code : ",code)
        if code == 'outgoing':
            for line in lines:
                print("line : ",line)
                print(line.lot_id)
                q = self.env['stock.quant'].search([('lot_id','=',line.lot_id.id)])
                filter_record = q.filtered(lambda q: q.location_id.usage == 'internal' or (q.location_id.usage == 'transit' and q.location_id.company_id))
                if not filter_record:
                    filter_record.temp_quantity = True
                    print("q : ",q)
                    print("q.quantity : ", q.quantity)
                    print("IN OUTGONING")
                    q.quantity = 0 - q.quantity
                    # if q.quantity == 1:
                    #     print("IN OUTGONING")
                    #     q.quantity = 0 - line.quantity
        if code == 'incoming':
            for line in lines:
                print("line : ",line)
                print(line.lot_id)
                q = self.env['stock.quant'].search([('lot_id','=',line.lot_id.id)])
                print("q : ", q)
                filter_record = q.filtered(lambda q: q.location_id.usage == 'internal' or (q.location_id.usage == 'transit' and q.location_id.company_id))
                print("filter_record : ",filter_record)
                print("filter_record.quantity : ",filter_record.quantity)
                print("self.temp_quantity : ",self.temp_quantity)
                if filter_record.temp_quantity == False:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>self : ",self)
                    filter_record.temp_quantity = True
                    print("YESSSS")
                    print("IN INCOMONING")
                    filter_record.quantity = 0

                # if filter_record.quantity == 1:
                #     if self.temp_quantity == False:
                #         print("YESSSS")
                #         print("IN INCOMONING")
                #         filter_record.quantity = 0
                #         self.temp_quantity = True

        return res

    def _set_auto_lot(self):
        """
        Allows to be called either by button or through code
        """
        print("LOTTTT")
        if self.mrp_id.lot_producing_id:
            self.move_line_ids.lot_id = self.mrp_id.lot_producing_id







