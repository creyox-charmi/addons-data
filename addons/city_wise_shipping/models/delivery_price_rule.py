from odoo import fields, models, api
from odoo.tools import format_amount

class DeliveryPriceRule(models.Model):
    _inherit = 'delivery.price.rule'

    variable = fields.Selection(
        selection_add=[('city', 'City')],
        ondelete={'city': 'cascade'},
        help="Variable to use for the condition (e.g., weight, volume, or city).")
    city_id = fields.Many2one('shipping.city', string='City')

    # def _get_price(self, order):
    #     """Override to handle city-based pricing."""
    #     if self.variable == 'city' and order.partner_shipping_id.city:
    #         city = self.env['shipping.city'].search([('name', '=', order.partner_shipping_id.city)], limit=1)
    #         if city and city.id == self.city_id.id:
    #             return self.list_price
    #     return super()._get_price(order)

    @api.depends('variable', 'operator', 'max_value', 'list_base_price', 'list_price', 'variable_factor', 'currency_id',
                 'city_id')
    def _compute_name(self):
        super()._compute_name()
        for rule in self:
            if rule.variable == 'city' and rule.city_id:
                name = 'if city = %s then' % rule.city_id.name
                if rule.currency_id:
                    price = format_amount(self.env, rule.list_price, rule.currency_id)
                else:
                    price = "%.2f" % rule.list_price
                name = '%s fixed price %s' % (name, price)
                rule.name = name

    def _get_price(self, order):
        """Override to handle city-based pricing."""
        if self.variable == 'city' and order.partner_shipping_id.city:
            city = self.env['shipping.city'].search([('name', '=', order.partner_shipping_id.city)], limit=1)
            if city and city.id == self.city_id.id:
                return self.list_price
        return super()._get_price(order)