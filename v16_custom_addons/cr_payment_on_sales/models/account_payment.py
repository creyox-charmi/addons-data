# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import _, api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    cr_sale_order_id = fields.Many2one('sale.order',string='Sale Order Id',copy=False)



class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        if self.env.context.get('active_id'):
            account_id = self.env["account.move"].browse(self.env.context.get('active_id'))
            if account_id:
                sale_ids = account_id.line_ids.sale_line_ids.order_id
                for sale_id in sale_ids:
                    if sale_id:
                        if account_id.payment_state == 'paid':
                            sale_id.cr_payment_state = 'paid'
                        if account_id.payment_state == 'partial':
                            sale_id.cr_payment_state = 'partial_paid'
