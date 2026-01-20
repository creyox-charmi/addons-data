# -*- coding: utf-8 -*-
from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # CFE field is already added in cr_mrp_bom_evr_customisation
    # No additional changes needed