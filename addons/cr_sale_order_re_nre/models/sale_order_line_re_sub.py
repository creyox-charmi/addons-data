# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api

class SaleOrderLineRESub(models.Model):
    """RE Sub-lines for recurring deliveries"""
    _name = 'sale.order.line.re.sub'
    _description = 'Sale Order Line RE Sub Lines'
    _order = 'sale_line_id, sequence, id'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Sequence', default=10)
    everest_pn = fields.Char(string='Everest PN', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    remaining_qty_to_deliver = fields.Float(
        string='Remaining Qty to Deliver',
        compute='_compute_remaining_qty',
        store=True
    )
    qty_delivered = fields.Float(string='Delivered Qty', default=0.0)
    delivery_note_number = fields.Char(string='Delivery Note Number')
    required_delivery_date = fields.Date(string='Required Delivery Date')
    updated_delivery_date = fields.Date(string='Updated Delivery Date')
    sub_line_code = fields.Char(string='Sub Line Code')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('invoiced', 'Invoiced')
    ], string='Status', default='pending')


    @api.depends('quantity', 'qty_delivered')
    def _compute_remaining_qty(self):
        """Compute remaining quantity as (quantity - qty_delivered)."""
        for line in self:
            line.remaining_qty_to_deliver = line.quantity - line.qty_delivered
