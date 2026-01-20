# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from datetime import datetime
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_state = fields.Selection(
        selection=[
            ('no_invoice', 'No Invoice'),
            ('not_paid', 'Not Paid'),
            ('partially_paid', 'Partially Paid'),
            ('fully_paid', 'Fully Paid'),
            ('overdue', 'Overdue')
        ],
        string='Payment Status',
        readonly=True,
    )
    amount_due = fields.Monetary(string='Amount Due')
    invoice_payments_widget = fields.Binary(string='Payment Details', exportable=False,compute='_compute_invoice_payment_widget')
    total_amount = fields.Monetary(string='total_amount',compute='_compute_total_amount',store=True)

    @api.depends('tax_totals')
    def _compute_total_amount(self):
        """Compute the total amount and amount due for the sale order"""
        for record in self:
            total = record.tax_totals['amount_total']
            record.total_amount = total
            record.amount_due = total

    def action_register_payment(self):
        """Action to register payment on the invoice lines of the sale order"""
        return self.invoice_ids.line_ids.action_register_payment()

    @api.depends('invoice_ids.payment_state', 'invoice_ids.invoice_payments_widget','invoice_ids.invoice_date')
    def _compute_invoice_payment_widget(self):
        """Compute the invoice payments widget data based on the state of the invoices"""
        is_overdue = 0
        today_date = datetime.now().date()

        # Loop through all sale orders to check invoice states , If any overdue invoices are found, set the payment state of the order to 'overdue'
        for order in self:
            for invoice in order.invoice_ids:
                in_date = invoice.invoice_date
                if in_date:
                    if in_date < today_date:
                        if invoice.payment_state != 'paid':
                            is_overdue = is_overdue + 1

            if is_overdue != 0:
                order.payment_state = 'overdue'

        # compute the payment details widget for invoice payments
        for order in self:
            payments_widget_data = {'title': 'Less Payment', 'outstanding': False, 'content': []}
            seen_references = set()

            for invoice in order.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
                if invoice.invoice_payments_widget:
                    invoice_widget_data = invoice.invoice_payments_widget

                    for entry in invoice_widget_data.get('content', []):
                        if entry['partial_id'] not in seen_references:
                            payments_widget_data['content'].append(entry)
                            seen_references.add(entry['partial_id'])

            order.invoice_payments_widget = payments_widget_data if payments_widget_data['content'] else False


