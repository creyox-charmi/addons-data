# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo.exceptions import ValidationError
from odoo import api, fields, models, tools, _


class Product_pricelist_items(models.Model):
    _inherit = "product.pricelist.item"

    uom_id = fields.Many2one("uom.uom", "Pricelist UOM")

    @api.constrains("uom_id")
    def _check_uom_id(self):
        if not self.uom_id:
            raise ValidationError(_("add pricelist in uom"))

    def check_get_price(self, uom=False, product=False):
        if product:
            price = product.list_price
        else:
            price = False

        if self.pricelist_id:
            if uom:
                if product:
                    for item in self.pricelist_id.item_ids:
                        if uom.id == item.uom_id.id:
                            if (
                                item.applied_on == "2_product_category"
                                and product.product_tmpl_id.categ_id.id
                                == item.categ_id.id
                            ):
                                price = item.fixed_price
                            elif item.applied_on == "1_product" and (
                                product.product_tmpl_id.id == item.product_tmpl_id.id
                            ):
                                price = item.fixed_price
                            elif item.applied_on == "0_product_variant" and (
                                product.product_tmpl_id.id == item.product_tmpl_id.id
                            ):
                                price = item.fixed_price
                            elif item.applied_on == "3_global":
                                price = item.fixed_price

        return price
