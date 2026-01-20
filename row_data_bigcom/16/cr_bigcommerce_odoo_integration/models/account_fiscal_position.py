# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import fields, models

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    bigcommerce_zone_id = fields.Char(
        string='BigCommerce Tax Zone ID',
        help='ID of the tax zone from BigCommerce (e.g., 1 for Default Zone).'
    )
    bigcommerce_store_id = fields.Many2one(
        comodel_name='bigcommerce.store',
        string='BigCommerce Store',
        help='The BigCommerce store associated with this fiscal position.'
    )