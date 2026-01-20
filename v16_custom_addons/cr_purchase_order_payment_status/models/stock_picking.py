# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields,api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """Override the 'button_validate' method , If there is a purchase order linked, set its payment state to 'no_bill'"""
        res = super(StockPicking, self).button_validate()

        if self.purchase_id:
            self.purchase_id.payment_state = 'no_bill'

        return res
