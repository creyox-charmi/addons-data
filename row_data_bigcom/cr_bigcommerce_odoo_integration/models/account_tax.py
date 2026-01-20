from odoo import fields, models

class AccountTax(models.Model):
    _inherit = 'account.tax'

    bigcommerce_tax_class_id = fields.Char(
        string='BigCommerce Tax Class ID',
        help='ID of the tax class from BigCommerce (e.g., 0 for Default Tax Class).'
    )
    bigcommerce_store_id = fields.Many2one(
        comodel_name='bigcommerce.store',
        string='BigCommerce Store',
        help='The BigCommerce store associated with this tax.'
    )