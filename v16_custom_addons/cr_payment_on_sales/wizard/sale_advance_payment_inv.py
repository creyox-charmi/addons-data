# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import _, api, fields, models

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self,sale_orders):
        invoices = super()._create_invoices(sale_orders)
        for order in sale_orders:
            if order.cr_payment_state == 'paid':
                for invoice in (order.invoice_ids & invoices):
                    invoice.action_post()
                    lines = order.cr_account_payment_line.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable') and not line.reconciled)
                    lines += invoice.line_ids.filtered(lambda line: line.account_id.id in lines.account_id.ids and not line.reconciled)
                    return lines.reconcile()
            if order.cr_payment_state == 'partial_paid':
                for invoice in (order.invoice_ids & invoices):
                    invoice.action_post()
                    lines = order.cr_account_payment_line.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable') and not line.reconciled)
                    lines += invoice.line_ids.filtered(lambda line: line.account_id.id in lines.account_id.ids and not line.reconciled)
                    return lines.reconcile()
        
        return invoices