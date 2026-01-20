# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields

class BigCommerceOrderStatus(models.Model):
    _name = 'bigcommerce.order.status'
    _description = 'BigCommerce Order Status'
    _rec_name = 'name'
    _order = 'order'

    store_id = fields.Many2one('bigcommerce.store', string="BigCommerce Store", required=True, ondelete='cascade')
    bigcommerce_status_id = fields.Integer(string="BigCommerce Status ID", required=True)
    name = fields.Char(string="Name", required=True)
    system_label = fields.Char(string="System Label")
    custom_label = fields.Char(string="Custom Label")
    system_description = fields.Text(string="System Description")
    order = fields.Integer(string="Order")
