# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import _, api, fields, models, SUPERUSER_ID

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        """Override method to set payment state to 'not_paid' when invoice is created"""
        res = super(SaleAdvancePaymentInv,self).create_invoices()
        if self.sale_order_ids:
            self.sale_order_ids.payment_state = 'not_paid'

        return res
