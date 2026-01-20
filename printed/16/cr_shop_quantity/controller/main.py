from docutils.parsers.rst.directives.misc import Class
from odoo import http
from odoo.http import request
import json

from odoo.http import request, route, Controller

from odoo.addons.sale.controllers.variant import VariantController


# class CustomWebsiteSaleVariantController(VariantController):
#
#     def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
#         print("before")
#         values = super().get_combination_info( product_template_id, product_id, combination, add_qty, pricelist_id, **kw)
#         print("product_template_id : ",product_template_id)
#         print("product_id : ", product_id)
#         print("pricelist_id : ", pricelist_id)
#         pricelist = pricelist_id
#         product_template = request.env['product.template'].search([('id','=',product_template_id)])
#         data = []
#         for price in pricelist.item_ids:
#             if price.applied_on == '3_global':
#                 print("All Products")
#                 data.append(price.id)
#             elif price.applied_on == '2_product_category':
#                 print("Product Category")
#                 if product_id:
#                     if price.product_id == product_id :
#                         if price.categ_id == product_id.categ_id.id:
#                             data.append(price.id)
#
#                 else:
#                     if price.product_tmpl_id == product_template_id :
#                         if price.categ_id == product_template.categ_id.id:
#                             data.append(price.id)
#
#             elif price.applied_on == '1_product':
#                 print("Product template")
#                 if price.product_tmpl_id == product_template:
#                     data.append(price.id)
#
#             else:
#                 print(price.applied_on)
#                 if product_id:
#                     if price.product_id.id == product_id:
#                         data.append(price.id)
#
#         print("data : ",data)
#
#         final_pricelists = request.env['product.pricelist.item'].search(
#             [
#                 ('id','in',data)
#             ]
#         )
#         print('final_pricelists : ',final_pricelists)
#         values['final_pricelists'] = final_pricelists
#         print(values)
#         return values

# class CustomWebsiteSaleVariantController(Controller):
#
#     @route('/cr_shop_quantity/cr_price', type='json', auth='user', methods=['POST'], website=True)
#     def a(self, **kw):
#         print("call")
#         combination = {}
#         data = json.loads(request.httprequest.data.decode("UTF-8"))
#         print("data : ", data)
#         dict = data['params']
#         product_id = dict['product_id']
#         print('product_id : ', product_id)
#         productTemplateId = dict['productTemplateId']
#         print('productTemplateId : ', productTemplateId)
#
#         product = request.env['product.product'].search([('id', '=', product_id)])
#         product_template = request.env['product.template'].search([('id', '=', productTemplateId)])
#         print('product_template : ', product_template)
#         pricelist = request.env['website'].get_current_website().pricelist_id
#
#         data1 = []
#         for price in pricelist.item_ids:
#             if price.applied_on == '3_global':
#                 print("All Products")
#                 data1.append(price.id)
#             elif price.applied_on == '2_product_category':
#                 print("Product Category")
#                 if product_id:
#                     if price.product_id == product_id:
#                         if price.categ_id == product_id.categ_id.id:
#                             data1.append(price.id)
#
#                 else:
#                     if price.product_tmpl_id == product_template.id:
#                         if price.categ_id == product_template.categ_id.id:
#                             data1.append(price.id)
#
#             elif price.applied_on == '1_product':
#                 print("Product template")
#                 if price.product_tmpl_id == product_template:
#                     data1.append(price.id)
#
#             else:
#                 print(price.applied_on)
#                 if product_id:
#                     if price.product_id.id == product_id:
#                         data1.append(price.id)
#
#         print("data1 : ", data1)
#
#         final_pricelists = request.env['product.pricelist.item'].search(
#             [
#                 ('id', 'in', data1)
#             ]
#         )
#
#         print('final_pricelists : ', final_pricelists)
#         combination['carousel'] = request.env['ir.ui.view']._render_template(
#             'cr_shop_quantity.product_template_pricelist',
#             values={
#                 'final_pricelists': request.env['product.pricelist.item'].browse(data1),
#                 'product': request.env['product.template'].browse(productTemplateId),
#                 'product_variant': request.env['product.product'].browse(product_id),
#                 'website': request.env['website'].get_current_website(),
#             },
#         )
#         response_data = {
#             'final_pricelists': request.env['product.pricelist.item'].browse(data1),
#             'product': request.env['product.template'].browse(productTemplateId),
#             'product_variant': request.env['product.product'].browse(product_id),
#         }
#         print("response_data : ", response_data)
#
#         # return request.render('cr_shop_quantity.product_template_pricelist', response_data)
#         return combination

# class CustomWebsiteSaleVariantController(Controller):
#
#     @route('/cr_shop_quantity/cr_price', type='json', auth='user', methods=['POST'], website=True)
#     def a(self ,**kw):
#         print("call")
#         combination = []
#         dict = json.loads(request.httprequest.data.decode("UTF-8"))
#         print("data : ",dict)
#         # dict = data['params']
#         product_id = dict['product_id']
#         print('product_id : ',product_id)
#         productTemplateId = dict['productTemplateId']
#         print('productTemplateId : ',productTemplateId)
#
#         product = request.env['product.product'].search([('id','=',product_id)])
#         product_template = request.env['product.template'].search([('id','=',productTemplateId)])
#         print('product_template : ', product_template)
#         pricelist = request.env['website'].get_current_website().pricelist_id
#
#         data1 = []
#         for price in pricelist.item_ids:
#             if price.applied_on == '3_global':
#                 print("All Products")
#                 data1.append(price.id)
#             elif price.applied_on == '2_product_category':
#                 print("Product Category")
#                 if product_id:
#                     if price.product_id == product_id:
#                         if price.categ_id == product_id.categ_id.id:
#                             data1.append(price.id)
#
#                 else:
#                     if price.product_tmpl_id == product_template.id:
#                         if price.categ_id == product_template.categ_id.id:
#                             data1.append(price.id)
#
#             elif price.applied_on == '1_product':
#                 print("Product template")
#                 if price.product_tmpl_id == product_template:
#                     data1.append(price.id)
#
#             else:
#                 print(price.applied_on)
#                 if product_id:
#                     if price.product_id.id == product_id:
#                         data1.append(price.id)
#
#         print("data1 : ", data1)
#
#         final_pricelists = request.env['product.pricelist.item'].search(
#             [
#                 ('id', 'in', data1)
#             ]
#         )
#
#         print('final_pricelists : ',final_pricelists)
#         response_data = {
#             'final_pricelists': request.env['product.pricelist.item'].browse(data1),
#             'product':request.env['product.template'].browse(productTemplateId),
#             'product_variant': request.env['product.product'].browse(product_id),
#         }
#
#
#
#         return request.render('cr_shop_quantity.product_template_pricelist',response_data)


# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo.http import request, route, Controller


class CustomWebsiteSaleVariantController(Controller):

    @route('/cr_shop_quantity/cr_price', type='json', auth='public', methods=['POST'], website=True)
    def a(self, product_template_id, product_id, combination, add_qty, parent_combination=None, **kwargs):
        print("yes calll")
        product_template = request.env['product.template'].browse(
            product_template_id and int(product_template_id))

        print('product_template : ',product_template)

        cr_combination_info = product_template._get_combination_info(
            combination=request.env['product.template.attribute.value'].browse(combination),
            product_id=product_id and int(product_id),
            add_qty=add_qty and float(add_qty) or 1.0,
            parent_combination=request.env['product.template.attribute.value'].browse(parent_combination),
        )

        print("cr_combination_info :  ",cr_combination_info)

        pricelist = request.env['website'].get_current_website().pricelist_id
        product_id = cr_combination_info['product_id']
        data = []
        for price in pricelist.item_ids:
            if price.applied_on == '3_global':
                data.append(price.id)
            elif price.applied_on == '2_product_category':
                if cr_combination_info['product_id']:
                    if price.product_id == product_id:
                        if price.categ_id == product_id.categ_id.id:
                            data.append(price.id)

                else:
                    if price.product_tmpl_id == product_template.id:
                        if price.categ_id == product_template.categ_id.id:
                            data.append(price.id)

            elif price.applied_on == '1_product':
                if price.product_tmpl_id == product_template:
                    data.append(price.id)

            else:
                if cr_combination_info['product_id']:
                    if price.product_id.id == product_id:
                        data.append(price.id)

        final_pricelists = request.env['product.pricelist.item'].search(
            [
                ('id', 'in', data)
            ]
        )

        cr_combination_info['carousel'] = request.env['ir.ui.view']._render_template(
            'cr_shop_quantity.product_template_pricelist',
            values={
                'product': product_template,
                'product_variant': request.env['product.product'].browse(cr_combination_info['product_id']),
                'website': request.env['website'].get_current_website(),
                'final_pricelists': final_pricelists
            },
        )
        print("final : ",cr_combination_info)

        return cr_combination_info
