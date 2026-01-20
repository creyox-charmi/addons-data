from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class CustomWebsiteSale(WebsiteSale):
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap="sitemap_shop")
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        print("in shop")
        # Call the original shop method first to get the usual setup
        response = super(CustomWebsiteSale, self).shop(page, category, search, min_price, max_price, ppg, **post)
        print(response)

        # Get the current user and filter selected products (only the ones the user selected)
        user = request.env.user
        selected_products = user.cr_product_ids
        print(selected_products)

        # Now filter the products in the response based on the selected ones
        if selected_products:
            print("enter................................")
            # Modify the products list in the response to show only the selected products
            response.qcontext['products'] = [product for product in response.qcontext['products'] if product.id in selected_products.ids]
            print(response.qcontext['products'])

        print(request.httprequest.args)


        return response
