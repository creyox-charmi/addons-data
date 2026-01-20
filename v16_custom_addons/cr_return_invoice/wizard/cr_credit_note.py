# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import _, api, fields, models


class CrCreditNote(models.TransientModel):
    _name = 'cr.credit.note'


    date = fields.Date(string='Refund date', default=fields.Date.context_today)
    reason = fields.Char(string='Reason')
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='User Specific Journal',
        required=True,
        readonly=False,
        store=True,
        domain="[('type','=','sale')]"
    )
    srp_id = fields.Many2one(comodel_name='stock.return.picking',
        string='User Specific Journal',)


    def action_reverse(self):
        ctx = dict(self.env.context)
        default_partner_id = ctx.get('default_partner_id')
        new_picking_id = ctx.get('new_picking_id')

        ctx.update({
            'new_picking_id': new_picking_id,
            'default_partner_id': default_partner_id,
            'search_default_picking_type_id': 1,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_planning_issues': False,
            'search_default_available': False,
            'date':self.date,
            'reason':self.reason,
            'journal_id':self.journal_id.id,
        })

        return {
            'name': _('Returned Picking'),
            'view_mode': 'form,tree,calendar',
            'res_model': 'stock.picking',
            'res_id': new_picking_id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }


