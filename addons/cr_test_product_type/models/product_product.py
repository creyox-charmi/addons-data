# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, api,fields

class ProductProduct(models.Model):
    _inherit = "product.product"

    type = fields.Selection(
        string="Inventory Managed Item",
        help="Goods are tangible materials and merchandise you provide.\n"
             "A service is a non-material product you provide.",
        selection=[
            ('consu', "Goods"),
            ('service', "Service"),
        ],
        required=True,
    )
