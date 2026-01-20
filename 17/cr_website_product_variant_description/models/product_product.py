# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    cr_description = fields.Html(string='Description')

    def get_des(self):
        flag = 0
        if self.cr_description:
            if self.cr_description != '<p><br></p>':
                flag = 1
        return flag