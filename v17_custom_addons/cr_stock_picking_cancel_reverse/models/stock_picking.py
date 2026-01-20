# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from importlib.resources import _
from odoo import models, fields, api
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = 'stock.picking'

    def action_reset_to_draft(self):
        """Reset the state of all associated moves back to 'draft'"""
        if self.state == 'done':
            self.action_cancel()
        self.state = 'draft'
        for move in self.move_ids:
            move.state = 'draft'
        for move_line in self.move_line_ids:
            move_line.state = 'draft'
        context = dict(self._context)
        context['reset_to_draft'] = True
        self.with_context(context)._compute_state()

    def _compute_state(self):
        if self._context.get('reset_to_draft'):
            self.state = 'draft'
        else:
            super(Picking, self)._compute_state()

    def c_action_cancel(self):
        """action to cancel a picking and its associated moves"""
        for picking in self:
            if picking.state == 'done':
                picking.update({"state": "cancel"})
                # for move in picking.move_ids:
                    # move.write({'state': 'cancel'})

                for move in picking.move_ids:
                    location_id = move.location_id
                    lot_id = None

                    if move.move_line_ids:
                        lot_ids = [line.lot_id.id for line in move.move_line_ids if line.lot_id]
                        lot_id = lot_ids[0] if lot_ids else None

                    if lot_id:
                        self._update_quantities(move.product_id, move.product_uom_qty, move.picking_type_id.code,
                                                location_id, lot_id)
                    else:
                        for move_line in picking.move_line_ids:
                            move_line.write(
                                {
                                    "quantity": 0.00,
                                }
                            )
                            move_line.move_id.update({"state": "cancel"})

                picking.write({'state': 'cancel'})

        return True

    def _update_quantities(self, product, quantity, picking_type_code, location_id, lot_id=None):
        """method to update stock quantities based on product movement"""
        if not location_id:
            raise UserError(_("No location specified for quantity update."))

        if picking_type_code == 'outgoing':
            if lot_id:
                stock_quants = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', location_id.id),
                    ('lot_id', '=', lot_id)
                ])

                for quant in stock_quants:
                    quant.sudo().write({
                        'quantity': quant.quantity + quantity
                    })

        elif picking_type_code == 'incoming':
            package_id = self.move_ids.move_line_ids and self.move_ids.move_line_ids[0].package_id.id
            if lot_id:
                stock_quants = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', self.location_dest_id.id),
                    ('lot_id', '=', lot_id),
                    ('owner_id', '=', self.move_ids.restrict_partner_id.id),
                    ('package_id', '=', package_id),
                ])

                for quant in stock_quants:
                    quant.sudo().write({
                        'quantity': quant.quantity - quantity
                    })
