# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models

class AccountMove(models.Model):
    _inherit="account.move"

    def js_td_remove_outstanding_partials(self,partial_ids):
        ''' Called by the 'payment' widget to remove a reconciled entries to the present Sales order.

        :param partial_ids: The ids of an existing partials reconciled with the current Sales order.
        '''
        self.ensure_one()
        partials = self.env['account.partial.reconcile'].browse(partial_ids)
        return partials.unlink()