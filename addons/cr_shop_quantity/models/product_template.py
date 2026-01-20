# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    min_sale_qty = fields.Integer("Min Sale Qty")
    max_sale_qty = fields.Integer("Max Sale Qty")
    qty_steps = fields.Integer("Quantity Steps")

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        parent_combination=False,
        only_template=False,
    ):
        ref = super()._get_combination_info(
            combination, product_id, add_qty, parent_combination, only_template
        )
        p = self.env["product.product"].search([("id", "=", ref["product_id"])])

        pricelist = self.env["website"].get_current_website().pricelist_id
        data = []
        for price in pricelist.item_ids:
            if price.min_quantity > 0:
                if price.applied_on == "3_global":
                    pass
                elif price.applied_on == "2_product_category":
                    if p:
                        cr_product = self.env["product.product"].search(
                            [("id", "=", p.id)]
                        )
                        if price.categ_id.id == cr_product.categ_id.id:
                            data.append(price.id)

                elif price.applied_on == "1_product":
                    if price.product_tmpl_id == p.product_tmpl_id:
                        data.append(price.id)

                else:
                    if ref["product_id"]:
                        if price.product_id.id == ref["product_id"]:
                            data.append(price.id)

        final_pricelists = self.env["product.pricelist.item"].search(
            [("id", "in", data)]
        )
        ref["final_pricelists"] = len(final_pricelists)
        return ref
