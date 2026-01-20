from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_delivery_methods(self):
        """Filter delivery methods based on city in pricing rules."""
        available_carriers = super()._get_delivery_methods()
        if not self.partner_id.city:
            return available_carriers
        city = self.env['shipping.city'].search([('name', '=', self.partner_id.city)], limit=1)
        if not city:
            return available_carriers
        return available_carriers.filtered(
            lambda c: c.delivery_type != 'base_on_rule' or any(
                rule.variable == 'city' and rule.city_id == city
                for rule in c.price_rule_ids
            )
        )