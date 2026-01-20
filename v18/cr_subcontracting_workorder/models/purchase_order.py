# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _

class Purchase(models.Model):
    _inherit = "purchase.order"

    workorder_id = fields.Many2one("mrp.workorder", string="Work Order")
    mrp_id = fields.Many2one("mrp.production", string="Manufacturing")


    def button_confirm(self):
        ref = super(Purchase,self).button_confirm()
        picking = self.env['stock.picking'].search([
            ('origin','=',self.name)
        ])
        if picking:
            if picking.state == 'draft':
                picking.action_confirm()

        return ref
