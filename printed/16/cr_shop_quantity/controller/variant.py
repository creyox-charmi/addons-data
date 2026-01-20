from odoo import http
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.http import request


class WebsiteSaleVariant(WebsiteSaleVariantController):

    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, **kw):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """
        print("aaaa")
        values = super().get_combination_info( product_template_id, product_id, combination, add_qty, **kw)
        print("product_template_id : ", product_template_id)
        print("product_id : ", product_id)
        print("pricelist_id : ", request.env['website'].get_current_website().pricelist_id)

        pricelist = request.env['website'].get_current_website().pricelist_id
        product_template = request.env['product.template'].search([('id', '=', product_template_id)])
        data = []
        for price in pricelist.item_ids:
            if price.applied_on == '3_global':
                print("All Products")
                data.append(price.id)
            elif price.applied_on == '2_product_category':
                print("Product Category")
                if product_id:
                    if price.product_id == product_id:
                        if price.categ_id == product_id.categ_id.id:
                            data.append(price.id)

                else:
                    if price.product_tmpl_id == product_template_id:
                        if price.categ_id == product_template.categ_id.id:
                            data.append(price.id)

            elif price.applied_on == '1_product':
                print("Product template")
                if price.product_tmpl_id == product_template:
                    data.append(price.id)

            else:
                print(price.applied_on)
                if product_id:
                    if price.product_id.id == product_id:
                        data.append(price.id)

        print("data : ", data)

        final_pricelists = request.env['product.pricelist.item'].search(
            [
                ('id', 'in', data)
            ]
        )
        print('final_pricelists : ', final_pricelists)
        values['final_pricelists'] = final_pricelists
        print(values)

        # First, call the parent method using super()
        # combination = super(WebsiteSaleVariantController, self).get_combination_info_website(
        #     product_template_id, product_id, combination, add_qty, **kw
        # )
        #
        # # Now, add additional values to the combination object
        # # Example: Add the current product's available stock
        # product = request.env['product.product'].browse(product_id)
        # combination['stock_quantity'] = product.qty_available
        #
        # # Example: Add the current product's price
        # combination['product_price'] = product.lst_price
        #
        # # Example: Add a custom message or flag (can be based on some condition)
        # combination['custom_message'] = "Special offer on this product!" if product.lst_price < 50 else ""
        #
        # # Optionally, you can add any additional logic here to enrich the combination further
        # # For example, adding more product details or custom fields.
        #
        # # Optionally, use google analytics or other logic here, depending on your needs
        # if request.website.google_analytics_key:
        #     combination['product_tracking_info'] = request.env['product.template'].get_google_analytics_data(
        #         combination)
        #
        # # Render the carousel view if needed
        # if request.website.product_page_image_width != 'none' and not request.env.context.get('website_sale_no_images',
        #                                                                                       False):
        #     carousel_view = request.env['ir.ui.view']._render_template('website_sale.shop_product_images', values={
        #         'product': request.env['product.template'].browse(combination['product_template_id']),
        #         'product_variant': request.env['product.product'].browse(combination['product_id']),
        #         'website': request.env['website'].get_current_website(),
        #     })
        #     combination['carousel'] = carousel_view

        return values
