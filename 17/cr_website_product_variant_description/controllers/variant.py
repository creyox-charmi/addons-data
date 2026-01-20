from odoo.http import request, route, Controller

class CustomWebsiteSaleVariantController(Controller):

    @route('/cr_website_product_variant_description/cr_des', type='json', auth='public', methods=['POST'], website=True)
    def a(self, product_template_id, product_id, combination, add_qty, parent_combination=None,**kwargs):
        product_template = request.env['product.template'].browse(
            product_template_id and int(product_template_id))

        cr_combination_info = product_template._get_combination_info(
            combination=request.env['product.template.attribute.value'].browse(combination),
            product_id=product_id and int(product_id),
            add_qty=add_qty and float(add_qty) or 1.0,
            parent_combination=request.env['product.template.attribute.value'].browse(parent_combination),
        )

        cr_combination_info['carousel'] = request.env['ir.ui.view']._render_template(
            'cr_website_product_variant_description.change_description',
            values={
                'product_variant': request.env['product.product'].browse(cr_combination_info['product_id']),
            },
        )

        return cr_combination_info

