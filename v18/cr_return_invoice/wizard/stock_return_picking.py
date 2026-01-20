# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import _, api, fields, models

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'


    def return_with_credit_note(self):
        for wizard in self:
            new_picking_id = wizard._create_return()
            ctx = dict(self.env.context)
            ctx.update({
                'new_picking_id': new_picking_id.id,
            })

            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'cr.credit.note',
                'views': [(False, 'form')],
                'target': 'new',
                'context': ctx,  # Pass the updated context with new_picking_id and other default values
            }

