# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    bigcommerce_store_id = fields.Many2one(
        'bigcommerce.store',
        string="BigCommerce Store",
        help="The Delivery belongs to."
    )