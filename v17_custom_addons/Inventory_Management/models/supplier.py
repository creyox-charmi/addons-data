from email.policy import default

from fields.extras import ValidationError
from odoo import api, fields, models, _

class Product(models.Model):
    """_name is display in the url when we are open department(table) of models(database) """
    _name = 'cr.inventory.supplier'
    _description = 'Supplier'

    name = fields.Char(string='Supplier Name', required=True)
    contact_info = fields.Char(string='Contact Information')
    state_id = fields.Many2one('res.country.state',
                               string="state_id")
    country_id = fields.Many2one('res.country',
                                 string="country_id")
    product_ids = fields.One2many('cr.inventory.product', 'supplier_id', string='Products')
    active = fields.Boolean(string="active",
                            default=True)

    @api.constrains('contact_info')
    def _check_contact_fields(self):
        for record in self:
            if len(record.contact_info) != 10:
                raise ValidationError("Invalid mobile Number!")