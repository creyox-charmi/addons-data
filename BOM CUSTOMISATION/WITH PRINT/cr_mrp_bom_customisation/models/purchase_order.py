# models/purchase_order.py
from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    cfe_project_location_id = fields.Many2one(
        'stock.location',
        string='CFE Project Location',
        domain=[('usage', '=', 'production')],
        help='Destination location for Customer Furnished Equipment'
    )
    production_id = fields.Many2one(
        'mrp.production',
        string="Manufacturing Order",
        help="Custom link between PO and MO"
    )
