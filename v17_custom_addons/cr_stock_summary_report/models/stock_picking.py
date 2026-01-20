# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def action_wizard_open(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cr.stock.summary',
            'views': [(False, 'form')],
            'target': 'current',
        }