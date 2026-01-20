# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class CustomWebsiteSale(WebsiteSale):

    @http.route(['/shop'], type='http', auth="public", website=True, sitemap=True)
    def shop(self, **post):
        """
        Overrides the default shop route to update the multi-quantity 
        product values for the current website.

        This method:
        - Fetches the current website.
        - Retrieves all product templates and updates their 
          multi-quantity product values by calling the `set_multi_quantity_product` method.
        - Calls the original shop method from the parent class and returns its response.

        :param post: Dictionary of additional keyword arguments passed to the route.
        :return: The response of the original `shop` method after updating product quantities.
        """
        current_website = request.website
        products = request.env['product.template'].search([])

        # Set the multi-quantity product value for each product
        for product in products:
            product.set_multi_quantity_product(current_website.id)

        # Call the parent shop method and return the response
        response = super(CustomWebsiteSale, self).shop(**post)

        return response
