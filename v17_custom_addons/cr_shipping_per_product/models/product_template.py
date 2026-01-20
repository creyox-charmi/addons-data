# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cr_delivery_carrier_ids = fields.Many2many(comodel_name='delivery.carrier',string='Allowed Delivery Methods')