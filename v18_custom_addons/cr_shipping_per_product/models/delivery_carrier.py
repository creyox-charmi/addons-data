# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    cr_product_template_ids = fields.Many2many(comodel_name='product.template',string='cr_product_template_ids')