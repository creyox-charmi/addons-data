from odoo import models, fields, api

class NRESubLineWizardLine(models.TransientModel):
    """Wizard Lines for NRE Sub-line"""
    _name = 'sale.order.line.nre.sub.wizard.line'
    _description = 'NRE Sub-line Wizard Line'

    wizard_id = fields.Many2one(
        'sale.order.line.nre.sub.wizard',
        string="Wizard",
        ondelete="cascade"
    )

    everest_pn = fields.Char(string="Everest PN")
    product_id = fields.Many2one('product.product', string="Product")
    billing_percentage = fields.Float(string="Billing %", required=True)
    sub_line_description = fields.Text(string="Sub-line Description")
    sub_line_code = fields.Char(string="Sub Line Code")
    required_delivery_date = fields.Date(string="Required Delivery Date")
    updated_delivery_date = fields.Date(string="Updated Delivery Date")