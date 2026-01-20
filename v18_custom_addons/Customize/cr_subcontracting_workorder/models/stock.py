# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _


class Stock(models.Model):
    _inherit = "stock.picking"

    workorder_id = fields.Many2one("mrp.workorder", string="Work Order")
    mrp_id = fields.Many2one("mrp.production", string="Manufacturing")
    temp_quantity = fields.Boolean(string='temp_quantity', default=False)

    def _return_subcontracting_picking(self, po):
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
        super_picking = super(Stock, self)._action_done()
        for rec in self:
            if rec.picking_type_id and rec.picking_type_id.code == "outgoing":
                rec._return_subcontracting_picking(rec.origin)
        return super_picking

    def action_confirm(self):
        for move in self.move_ids_without_package:
            if move.product_id:
                if move.product_uom_qty:
                    move.quantity = move.product_uom_qty
        res = super(Stock, self).action_confirm()

    def button_validate(self):
        self._set_auto_lot()
        res = super(Stock, self).button_validate()
        lines = self.move_line_ids
        code = self.picking_type_id.code
        if code == 'outgoing':
            for line in lines:
                q = self.env['stock.quant'].search([('lot_id', '=', line.lot_id.id)])
                filter_record = q.filtered(lambda q: q.location_id.usage == 'internal' or (
                            q.location_id.usage == 'transit' and q.location_id.company_id))
                if not filter_record:
                    filter_record.temp_quantity = True
                    q.quantity = 0 - q.quantity

        if code == 'incoming':
            for line in lines:
                q = self.env['stock.quant'].search([('lot_id', '=', line.lot_id.id)])
                filter_record = q.filtered(lambda q: q.location_id.usage == 'internal' or (
                            q.location_id.usage == 'transit' and q.location_id.company_id))
                if filter_record.temp_quantity == False:
                    filter_record.temp_quantity = True
                    filter_record.quantity = 0

        return res

    def _set_auto_lot(self):
        """
        Allows to be called either by button or through code
        """
        if self.mrp_id.lot_producing_id:
            self.move_line_ids.lot_id = self.mrp_id.lot_producing_id
