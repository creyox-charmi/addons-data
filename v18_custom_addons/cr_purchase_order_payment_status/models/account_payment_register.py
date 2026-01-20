# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api
from datetime import datetime


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        """Method to create payments and update related purchase orders"""
        # Call the parent method to create payments
        res = super(AccountPaymentRegister, self).action_create_payments()

        # Split the communication field into individual elements for matching
        com = self.communication.split()

        # Search for account moves based on the communication names
        ac_move = self.env['account.move'].search([
            ('name','in',com)
        ])

        due = 0
        count = len(ac_move)
        is_overdue = 0
        today_date = datetime.now().date()

        # Loop through all account moves to calculate due amounts and check overdue status
        for move in ac_move:
            due = due + move.amount_residual

            if move.payment_state == 'paid':
                count = count - 1

            if move.invoice_date < today_date :
                if move.payment_state != 'paid':
                    is_overdue = is_overdue + 1

        # Loop through account moves again to update related purchase orders
        for move in ac_move:
            purchase = self.env['purchase.order'].search([
                ('invoice_ids', '=',move.id)
            ])
            purchase.amount_due = due

            if count == 0:
                purchase.payment_state = 'fully_paid'
            else:
                purchase.payment_state = 'partially_paid'

            if is_overdue != 0:
                purchase.payment_state = 'overdue'

            break

        return res

