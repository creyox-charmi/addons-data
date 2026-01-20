# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import api, fields, models, _

class ViewAccountPaymentRegisterForm(models.TransientModel):
    _inherit = "account.payment.register"

    cr_add_cash_register_entry = fields.Boolean(string='Add Cash Register Entry')
    cr_cash_register_option = fields.Selection(
        [
        ('using cash register', 'Using Cash Register'),
        ('without using cash register', 'Without Using Cash Register')
        ],
        string='Cash Register Option')
    cr_cash_register_id = fields.Many2one(comodel_name='account.bank.statement',string='Cash Register')

    def action_create_payments(self):
        payment = super(ViewAccountPaymentRegisterForm, self).action_create_payments()
        self._create_bank_reconciliation_entry(payment)
        return payment

    def _create_bank_reconciliation_entry(self, payment):
        if self.cr_cash_register_id:
            bank_statement_line = {
                'payment_ref': self.communication,
                'partner_id': self.partner_id.id,
                'amount': self.amount,
                'journal_id': self.journal_id.id,
                'date': self.payment_date,
                'statement_id': self.cr_cash_register_id.id,
            }
        else:
            bank_statement_line = {
                'payment_ref': self.communication,
                'partner_id': self.partner_id.id,
                'amount': self.amount,
                'journal_id': self.journal_id.id,
                'date': self.payment_date,
            }

        self.env['account.bank.statement.line'].create(bank_statement_line)
        return True
