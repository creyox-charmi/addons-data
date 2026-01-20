from odoo import models, api,_
from odoo.exceptions import UserError

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def _get_price_available(self, order):
        """Override to pass partner and order_id in context to _get_price_from_picking."""
        print('YES OVERRIDE')
        self.ensure_one()
        self = self.sudo()
        order = order.sudo()
        total = weight = volume = quantity = wv = 0
        total_delivery = 0.0

        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            if line.product_id.type == "service":
                continue
            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty
            wv += (line.product_id.weight or 0.0) * (line.product_id.volume or 0.0) * qty
            quantity += qty
        total = (order.amount_total or 0.0) - total_delivery

        total = self._compute_currency(order, total, 'pricelist_to_company')
        weight = self.env.context.get('order_weight') or order.shipping_weight or weight

        # Prepare context with partner and order_id
        context = {
            'partner': order.partner_shipping_id,
            'order_id': order.id
        }
        print('Context passed to _get_price_from_picking:', context)

        # Call _get_price_from_picking with updated context
        return self.with_context(**context)._get_price_from_picking(total, weight, volume, quantity, wv=wv)

    def _is_available_for_order(self, order):
        """ Override of `delivery` to exclude regular delivery methods from Gelato orders and Gelato
        delivery methods from non-Gelato orders.

        :param sale.order order: The current order.
        :return: Whether the delivery method is available for the order.
        :rtype: bool
        """
        print('self : ', self)
        print('order : ', order)
        if self.name != 'City-Based Shipping':
            return False
        # is_gelato_order = any(order.order_line.product_id.mapped('gelato_product_uid'))
        # is_gelato_delivery = self.delivery_type == 'gelato'
        # if is_gelato_order and not is_gelato_delivery or not is_gelato_order and is_gelato_delivery:
        #     return False
        return super()._is_available_for_order(order)

    def available_carriers(self, partner, order):
        """ Override of `delivery` to filter out regular delivery methods from Gelato orders and
        Gelato delivery methods from non-Gelato orders.

        :param res.partner partner: The partner to check.
        :param sale.order order: The current order.
        :return: The available delivery methods.
        :rtype: delivery.carrier
        """
        available_delivery_methods = super().available_carriers(partner, order)
        # is_gelato_order = any(order.order_line.product_id.mapped('gelato_product_uid'))
        # if is_gelato_order:
        #     return available_delivery_methods.filtered(lambda m: m.delivery_type == 'gelato')
        # else:
        #     return available_delivery_methods.filtered(lambda m: m.delivery_type != 'gelato')
        return available_delivery_methods.filtered(lambda m: m.name == 'City-Based Shipping')

    @api.model
    def _match_address(self, partner):
        """Override to include city-based matching via pricing rules."""
        print('Yes Partner')
        print('partner : ',partner,' ',partner.city)
        self.ensure_one()
        if not partner or not partner.city:
            return super()._match_address(partner)
        city = self.env['shipping.city'].search([('name', '=', partner.city)], limit=1)
        print('city : ',city)
        if not city:
            return super()._match_address(partner)
        # Check if any pricing rule matches the city
        if self.delivery_type == 'base_on_rule' and any(
            rule.variable == 'city' and rule.city_id == city
            for rule in self.price_rule_ids
        ):
            print('TRUEEEEEEEEEE')
            return True
        return super()._match_address(partner)

    # def _get_price_from_picking(self, total, weight, volume, quantity, wv=0.):
    #     """Override to handle city-based pricing rules."""
    #     print('BEFORE...')
    #     price = 0.0
    #     criteria_found = False
    #     # order = self.env.context.get('order_id') and self.env['sale.order'].browse(self.env.context['order_id'])
    #     # print('order : ',order)
    #     city = False
    #     # if order and order.partner_shipping_id.city:
    #     #     print('order.partner_shipping_id.city : ',order.partner_shipping_id.city)
    #     #     city = self.env['shipping.city'].search([('name', '=', order.partner_shipping_id.city)], limit=1)
    #
    #     for line in self.price_rule_ids:
    #         if line.variable == 'city' and city and line.city_id == city:
    #             price = line.list_price
    #             criteria_found = True
    #             break
    #
    #     if not criteria_found:
    #         try:
    #             price = super()._get_price_from_picking(total, weight, volume, quantity, wv=wv)
    #             criteria_found = True
    #         except UserError:
    #             pass  # Let the error be raised below if no criteria found
    #
    #     if not criteria_found:
    #         raise UserError(_("No matching pricing rule found for the current order."))
    #
    #     return price

    def _get_price_from_picking(self, total, weight, volume, quantity, wv=0.):
        """Override to handle city-based pricing rules."""
        print('BEFORE...')
        price = 0.0
        criteria_found = False

        city = False

        print('1: ',self.env.user,' ',self.env.user.name)
        print('2: ', self.env.user.city)

        # city = self.env['shipping.city'].search([('name', '=', self.env.user.city)], limit=1)

        partner = self.env.context.get('partner')
        if not partner and self.env.context.get('order_id'):
            order = self.env['sale.order'].browse(self.env.context.get('order_id'))
            partner = order.partner_shipping_id
            # city = partner.city
        city = self.env['shipping.city'].search([('name', '=', partner.city)], limit=1)
        print('Partner:', partner, 'Partner ID:', partner.id if partner else 'No Partner', 'City:',
              partner.city if partner else 'No City')
        print('city : ',city)
        print('USER : ',    self.env.user)
        for line in self.price_rule_ids:
            print('line : ',line)
            print('line.variable : ',line.variable)
            print('line.city_id : ', line.city_id)
            if line.variable == 'city' and line.city_id and line.city_id == city:
                print('yes city')
                price = line.list_price
                print('price : ', price)
                criteria_found = True
                break

        if not criteria_found:
            try:
                price = super()._get_price_from_picking(total, weight, volume, quantity, wv=wv)
                criteria_found = True
            except UserError:
                pass  # Let the error be raised below if no criteria found

        if not criteria_found:
            raise UserError(_("No matching pricing rule found for the current order."))

        return price