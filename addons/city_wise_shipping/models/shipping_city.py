from odoo import fields, models

class ShippingCity(models.Model):
    _name = 'shipping.city'
    _description = 'City for Shipping'

    name = fields.Char(string='City Name', required=True)
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country', required=True)