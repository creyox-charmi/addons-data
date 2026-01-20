
from odoo import models, fields,api



class ChangeStatus(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('sent', 'RFQ Sent'),
        ('waiting', 'Waiting For Approval'),
        ('reject','Reject'),
        ('purchase', 'Purchase Order')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    def button_confirm(self):
        for order in self:
            order.write({'state': 'waiting'})


