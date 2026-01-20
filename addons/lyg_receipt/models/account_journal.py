# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountJournal(models.Model):
    """Inherited AccountJournal for new fields."""
    _inherit = 'account.journal'

    means_of_payment = fields.Selection(
        [('1', 'Cash'), ('2', 'Check'), ('3', 'Credit Card'),
         ('4', 'Bank Transfer'), ('5', 'Gift Card'), ('6', 'Return Note'),
         ('7', 'Promissory Note'), ('8', 'Standing Order'), ('9', 'Other')],)