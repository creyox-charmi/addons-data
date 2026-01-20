from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    conf_method = fields.Selection([
        ('untaxed_amount', 'Untaxed amount'),
        ('total', 'Total')
    ], string='Approved Based On', default='untaxed_amount',
    help='Purchase Order Based On : Untaxed/ Total')