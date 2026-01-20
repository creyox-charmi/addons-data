# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.api import ValuesType, Self


class Purchase(models.Model):
    _inherit = "purchase.order"

    workorder_id = fields.Many2one("mrp.workorder", string="Work Order")
    mrp_id = fields.Many2one("mrp.production", string="Manufacturing")

    # @api.depends('mrp_id')
    # def assign_source_description(self):
    #     print('mrp : ',self.mrp_id)
    #
    #
    # def create(self, vals_list):
    #     print("before")
    #     ref = super(Purchase,self).create(vals_list)
    #     print('ref : ',ref)
    #     print('mrp_id : ', ref.mrp_id)
    #     ref.origin = ref.mrp_id.name
    #     print(">>",ref.order_line.product_id)
    #     print("after")
    #     return ref
