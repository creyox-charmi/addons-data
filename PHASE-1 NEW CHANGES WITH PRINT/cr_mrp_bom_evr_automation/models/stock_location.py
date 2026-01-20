# -*- coding: utf-8 -*-
from odoo import models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    # No additional changes needed, just ensure location_category field is accessible