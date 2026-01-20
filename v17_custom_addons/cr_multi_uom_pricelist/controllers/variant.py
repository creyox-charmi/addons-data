
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.variant import \
    WebsiteSaleVariantController


class CrVairant(WebsiteSaleVariantController):
    @http.route('/website_sale/get_combination_info', type='json',
                auth='public',
                methods=['POST'], website=True)
    def get_combination_info_website(
            self, product_template_id, product_id, combination, add_qty,
            uom=False,
            parent_combination=None,
            **kwargs
    ):
        print('enter')
        res = super(
            CrVairant, self).get_combination_info_website(
            product_template_id=product_template_id, product_id=product_id,
            combination=combination, add_qty=add_qty,
            uom=uom, parent_combination=parent_combination, **kwargs)
        p = request.env['product.template'].search([('id','=',product_template_id)])
        print(' p : ',p)
        uom = p.uom_id
        print("x : ",uom)
        # request.session['uom_id'] = uom
        if uom:
            print("yes uom")
            print('uom : ',uom)
            uom_id = request.env['uom.uom'].browse(int(uom))
            product = request.env['product.product'].sudo().browse(product_id)
            default_uom_qty = uom_id._compute_quantity(add_qty, product.uom_id)
            updated_price = res['list_price'] * default_uom_qty
            res.update({'price': updated_price})
        return res
