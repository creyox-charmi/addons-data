# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import config

class BigCommerceWebhook(models.Model):
    _name = 'bigcommerce.webhook'
    _description = 'BigCommerce Webhook'

    bigcommerce_store_id = fields.Many2one('bigcommerce.store', string='BigCommerce Store', required=True, ondelete='cascade')
    webhook_id = fields.Integer(string='Webhook ID', required=True)
    scope = fields.Char(string='Scope', required=True)
    destination = fields.Char(string='Destination URL', required=True)
    is_active = fields.Boolean(string='Is Active', default=True)
    created_at = fields.Integer(string='Created At')
    updated_at = fields.Integer(string='Updated At')