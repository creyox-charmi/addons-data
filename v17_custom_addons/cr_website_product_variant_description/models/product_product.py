# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    cr_description = fields.Html(string='Description')

    def get_description(self):
        print(self.cr_description)
        return self.cr_description