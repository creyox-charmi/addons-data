# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import _, api, fields, models
from odoo.tools import formatLang

class SaleOrder(models.Model):
    _inherit='sale.order'

    cr_show_register_payment = fields.Boolean(compute='_compute_cr_show_register_payment')
    cr_show_create_invoice = fields.Boolean(compute='_compute_cr_show_create_invoice')

    cr_payment_state = fields.Selection(selection=[('draft', 'Draft'),('partial_paid', 'Partial Paid'),('paid','Paid')], default='draft', compute='_compute_cr_payment', store=True, precompute=True, readonly=False)
    cr_amount_residual = fields.Monetary(string='Amount Due',compute='_compute_cr_payment', store=True, precompute=True)
    cr_invoice_payments_widget = fields.Binary(groups='account.group_account_invoice,account.group_account_readonly',compute='_compute_cr_invoice_payments_widget',exportable=False,)

    cr_account_payment_line = fields.One2many('account.payment','cr_sale_order_id',string='Payment line', copy=False)
    
    @api.depends('state','cr_account_payment_line','cr_account_payment_line.state','cr_account_payment_line.amount','invoice_ids.payment_state')
    def _compute_cr_payment(self):
        for order in self:
            cr_payment_state = 'draft'
            currency = order.currency_id
            total_paid = sum([payment.currency_id._convert(payment.amount,currency,order.currency_id) for payment in order.cr_account_payment_line.filtered(lambda pay: pay.state=='posted' and pay.payment_type=='inbound' and pay.partner_id.id == order.partner_id.id)])
            if total_paid:
                cr_payment_state = 'paid' if total_paid >= order.amount_total else 'partial_paid'

            if cr_payment_state == 'draft' and order.invoice_ids:
                if all(invoice.state == 'posted' and invoice.payment_state=='paid' for invoice in order.invoice_ids):
                    cr_payment_state = 'paid'
                elif any(invoice.state == 'posted' and invoice.payment_state in ('paid','partial') for invoice in order.invoice_ids):
                    cr_payment_state = 'partial_paid'

            order.cr_amount_residual = order.amount_total - total_paid
            order.cr_payment_state = cr_payment_state

    @api.depends('state','cr_payment_state')
    def _compute_cr_show_register_payment(self):
        for order in self:
            order.cr_show_register_payment = bool(order.state == 'sale' and order.cr_payment_state != 'paid' and not order.invoice_ids)

    @api.depends('cr_payment_state')
    def _compute_cr_show_create_invoice(self):
        for order in self:
            order.cr_show_create_invoice = bool(order.cr_payment_state == 'paid')

    @api.depends('cr_payment_state','cr_account_payment_line')
    def _compute_cr_invoice_payments_widget(self):
        for order in self:
            cr_invoice_payments_widget = False
            if order.cr_account_payment_line:
                payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
                if order.state in ('sale','done'):
                    reconciled_vals = []
                    for payment in order.cr_account_payment_line:
                        
                        for line in payment.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable')):
                                                    
                            if line.move_id.ref:
                                reconciliation_ref = '%s (%s)' % (line.move_id.name, line.move_id.ref)
                            else:
                                reconciliation_ref = line.move_id.name
                            if line.amount_currency and line.currency_id != line.company_id.currency_id:
                                foreign_currency = line.currency_id
                            else:
                                foreign_currency = False

                            reconciled_vals.append({
                                'name': line.name,
                                'journal_name': line.journal_id.name,
                                'company_name': line.journal_id.company_id.name if line.journal_id.company_id != order.company_id else None,
                                'amount': payment.amount,
                                'currency_id': payment.currency_id.id,
                                'date': line.date,
                                'partial_ids': (line.matched_debit_ids | line.matched_credit_ids).ids,
                                'account_payment_id': line.payment_id.id,
                                'payment_method_name': line.payment_id.payment_method_line_id.name,
                                'move_id': line.move_id.id,
                                'ref': reconciliation_ref,
                                # these are necessary for the views to change depending on the values
                                'is_exchange': False,
                                'is_td_reconciled':line.reconciled,
                                'cr_payment_state':str.capitalize(payment.state),
                                'amount_company_currency': formatLang(self.env, abs(line.balance), currency_obj=line.company_id.currency_id),
                                'amount_foreign_currency': foreign_currency and formatLang(self.env, abs(line.amount_currency), currency_obj=foreign_currency)
                            })
                    payments_widget_vals['content'] = reconciled_vals

                    if payments_widget_vals['content']:
                        cr_invoice_payments_widget = payments_widget_vals

            order.cr_invoice_payments_widget = cr_invoice_payments_widget

    def action_cr_register_payment_on_sale(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'cr.register.payment.wizard',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'context': {
                'default_sale_order_id': self[:1].id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
