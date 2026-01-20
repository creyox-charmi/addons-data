# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _update_nre_sub_lines_on_cancel(self):
        """Reset invoicing_status of related NRE sub-lines and wizard lines when invoice is cancelled."""
        for move in self:
            # Skip if not a customer invoice
            if move.move_type != 'out_invoice':
                continue

            # Find related NRE sub-lines linked to this invoice
            nre_sub_lines = self.env['sale.order.line.nre.sub'].search([
                ('invoice_id', '=', move.id)
            ])

            if not nre_sub_lines:
                continue

            # Reset invoicing_status and unlink invoice reference
            nre_sub_lines.write({
                'invoicing_status': 'to_invoice',
                'invoice_id': False,
                'invoiced_amount': 0.0,
            })


    def button_cancel(self):
        """Override cancel button to also reset NRE sub-line statuses."""
        res = super(AccountMove, self).button_cancel()
        self._update_nre_sub_lines_on_cancel()
        return res
