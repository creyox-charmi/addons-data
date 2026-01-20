# # -*- coding: utf-8 -*-
# # Part of Creyox Technologies

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json


class CrWebsiteForm(WebsiteSale):
    @http.route(['/cr_website_order_matrix_view/add_to_cart'], type='json', auth="public", methods=['POST'],
                website=True)
    def add_to_cart(self, **kwargs):
        data = json.loads(request.httprequest.data.decode("UTF-8"))
        total_products = len(data.get("combinations"))
        for i in range(total_products):
            comb = data.get("combinations")[i]
            string = comb.get("combinations")
            my_list = string.split()
            quantity = comb.get("quantity")
            product_custom_attribute_values = comb.get("product_custom_attribute_values")

            product_template = request.env['product.template'].search(
                [
                    ('id','=',data.get("productTemplateId"))
                ]
            )

            product = request.env['product.product'].search(
                [
                    ('name', '=', product_template.name)
                ]
            )

            dict = {}
            for p in product:
                count = 0
                for value in p.product_template_attribute_value_ids:
                    if value.name in my_list:
                        count = count + 1
                if count == len(my_list):
                    dict = {'product':p.name,'id':p}
                    break
            self.cart_update(
                product_id= dict['id'],
                add_qty= quantity,
                product_custom_attribute_values= product_custom_attribute_values,
            )
        url_dict = {'redirect_url': '/shop/cart'}
        return url_dict