# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo.http import request, route, Controller


class CustomWebsiteSaleVariantController(Controller):
    @route(
        "/cr_shop_quantity/cr_price",
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def a(
        self,
        product_template_id,
        product_id,
        combination,
        add_qty,
        parent_combination=None,
        **kwargs
    ):
        product_template = request.env["product.template"].browse(
            product_template_id and int(product_template_id)
        )

        cr_combination_info = product_template._get_combination_info(
            combination=request.env["product.template.attribute.value"].browse(
                combination
            ),
            product_id=product_id and int(product_id),
            add_qty=add_qty and float(add_qty) or 1.0,
            parent_combination=request.env["product.template.attribute.value"].browse(
                parent_combination
            ),
        )

        pricelist = request.env["website"].get_current_website().pricelist_id
        product_id = cr_combination_info["product_id"]
        data = []
        for price in pricelist.item_ids:
            if price.min_quantity > 0:
                if price.applied_on == "3_global":
                    data.append(price.id)
                elif price.applied_on == "2_product_category":
                    if cr_combination_info["product_id"]:
                        cr_product = request.env["product.product"].search(
                            [("id", "=", product_id)]
                        )
                        if price.categ_id.id == cr_product.categ_id.id:
                            data.append(price.id)
                        if price.product_id.id == product_id:
                            if price.categ_id.id == product_id.categ_id.id:
                                data.append(price.id)

                    else:
                        cr_product = request.env["product.template"].search(
                            [("id", "=", product_template.id)]
                        )
                        if price.categ_id.id == cr_product.categ_id.id:
                            data.append(price.id)
                        if price.product_tmpl_id.id == product_template.id:
                            if price.categ_id == product_template.categ_id.id:
                                data.append(price.id)

                elif price.applied_on == "1_product":
                    if price.product_tmpl_id == product_template:
                        data.append(price.id)

                else:
                    if cr_combination_info["product_id"]:
                        if price.product_id.id == product_id:
                            data.append(price.id)

        final_pricelists = request.env["product.pricelist.item"].search(
            [("id", "in", data)]
        )

        cr_combination_info["carousel"] = request.env["ir.ui.view"]._render_template(
            "cr_shop_quantity.product_template_pricelist",
            values={
                "product": product_template,
                "product_variant": request.env["product.product"].browse(
                    cr_combination_info["product_id"]
                ),
                "website": request.env["website"].get_current_website(),
                "final_pricelists": final_pricelists,
            },
        )
        return cr_combination_info
