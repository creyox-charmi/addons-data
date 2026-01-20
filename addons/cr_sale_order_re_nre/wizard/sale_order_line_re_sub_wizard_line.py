# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RESubLineWizardLine(models.TransientModel):
    _name = 'sale.order.line.re.sub.wizard.line'
    _description = 'RE Sub-line Wizard Line'

    wizard_id = fields.Many2one('sale.order.line.re.sub.wizard', string="Wizard", ondelete="cascade")
    everest_pn = fields.Char()
    quantity = fields.Float()
    qty_delivered = fields.Float()
    remaining_qty_to_deliver = fields.Float()
    required_delivery_date = fields.Date()
    updated_delivery_date = fields.Date()
    sub_line_code = fields.Char()
    delivery_note_number = fields.Char()
