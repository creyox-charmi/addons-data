# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = 'stock.picking'

    credit_note_count = fields.Integer(string="Invoice Count",default=1)
    credit_note_id = fields.Many2one('account.move', string='Credit Note', readonly=True)

    def action_view_credit_note(self):
        for picking in self:
            if not picking.credit_note_id:
                # Create the credit note if it doesn't exist
                credit_note = self._create_credit_note_from_picking(picking)

                # Link the credit note to this stock picking
                picking.credit_note_id = credit_note.id

            # Open the credit note form view
            return {
                'type': 'ir.actions.act_window',
                'name': _('Credit Note'),
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': picking.credit_note_id.id,
                'target': 'current',
            }

    def _create_credit_note_from_picking(self, picking):
        ctx = dict(self.env.context)
        reverse_date = fields.Date.from_string(ctx.get('date'))
        active_model = ctx.get('model')
        active_id = ctx.get('active_id')
        data = self.env['stock.picking'].search([('id','=',active_id)])
        sale = data.sale_id
        move = sale.invoice_ids
        # Make sure the picking is linked to a sale order
        if not sale:
            raise UserError(_('No sale order found for this picking.'))

        # Get the invoice related to the sale order
        invoice = move

        if not invoice:
            raise UserError(_('No open invoice found for this sale order.'))

        # Create the credit note (out_refund type)
        credit_note_vals = {
            'ref': _('Reversal of:  %(reason)s', reason=ctx.get('reason')),
            'date': reverse_date,
            'invoice_date_due': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (ctx.get('date') or move.date) or False,
            'journal_id': ctx.get('journal_id'),
            'partner_id': invoice.partner_id.id,
            'invoice_user_id': move.invoice_user_id.id,
            'move_type': 'out_refund',  # Credit note type
            'invoice_line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.product_id.lst_price,
                'name': line.name,
            }) for line in picking.move_ids_without_package],
        }

        # Create the credit note
        credit_note = self.env['account.move'].create(credit_note_vals)


        return credit_note