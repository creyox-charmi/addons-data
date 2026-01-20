# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import _, api, fields, models

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'


    def return_with_credit_note(self):
        for wizard in self:
            new_picking_id, pick_type_id = wizard._create_returns()

            ctx = dict(self.env.context)
            ctx.update({
                'search_default_picking_type_id': pick_type_id,
                'new_picking_id': new_picking_id,  # Explicitly pass new_picking_id
                'default_partner_id': self.picking_id.partner_id.id,
                'search_default_draft': False,
                'search_default_assigned': False,
                'search_default_confirmed': False,
                'search_default_ready': False,
                'search_default_planning_issues': False,
                'search_default_available': False,
            })

            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'cr.credit.note',
                'views': [(False, 'form')],
                'target': 'new',
                'context': ctx,  # Pass the updated context with new_picking_id and other default values
            }

