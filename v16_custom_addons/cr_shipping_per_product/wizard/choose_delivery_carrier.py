# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    cr_per_product_shipping_ids = fields.Many2many(comodel_name='cr.per.product.shipping',
                                                   string='cr_per_product_shipping_ids')
    cr_is_update = fields.Boolean(string='cr_is_update', compute='_compute_cr_is_update',
                                  store=True, )

    @api.depends('cr_per_product_shipping_ids')
    def _compute_cr_is_update(self):
        """This method computes the value of the 'cr_is_update' field based on the related shipping records"""
        price = 0  # Initialize the variable to accumulate total price

        # Iterate through each related 'cr.per.product.shipping' record
        for record in self.cr_per_product_shipping_ids:
            price += record.delivery_carrier_id.fixed_price  # Add the fixed price of each delivery carrier to the total price

        # Search for an existing delivery carrier with the name 'custom shipping'
        shipping = self.env['delivery.carrier'].search([('name', '=', 'custom shipping')])

        if shipping:
            # If a custom shipping carrier exists, update its price and associated product's price
            self.carrier_id = shipping  # Assign the existing shipping carrier
            shipping.fixed_price = price  # Set the fixed price for the carrier
            shipping.product_id.standard_price = price  # Update the standard price of the associated product
            shipping.product_id.lst_price = price  # Update the list price of the associated product
        else:
            # If no custom shipping carrier exists, create a new product and carrier with the calculated price
            product = self.env['product.product'].create({
                'name': 'custom shipping',  # Create a product named 'custom shipping'
                'standard_price': 0.0,  # Set the default standard price to 0
                'list_price': 0.0,  # Set the default list price to 0
            })

            # Create a new delivery carrier for the custom shipping
            ship = self.env['delivery.carrier'].create({
                'name': 'custom shipping',  # Assign the name 'custom shipping' to the new carrier
                'product_id': product.id  # Link the new product to this carrier
            })

            # Assign the newly created carrier to the 'carrier_id' field
            self.carrier_id = ship
            ship.fixed_price = price  # Set the fixed price for the new carrier
            ship.product_id.standard_price = price  # Set the standard price of the associated product
            ship.product_id.lst_price = price  # Set the list price of the associated product

        # Update the delivery price and display price for the shipping process
        self.delivery_price = price
        self.display_price = price

        # Mark the flag indicating that the update is complete
        self.cr_is_update = True
