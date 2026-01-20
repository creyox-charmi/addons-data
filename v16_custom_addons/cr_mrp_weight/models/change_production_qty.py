# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import api, fields, models, _


class ChangeProductionQty(models.TransientModel):
    _inherit = "change.production.qty"
    _description = "Change Production Qty"

    cr_weight = fields.Float("Weight")

    @api.onchange("product_qty")
    def _calculate_weight(self):
        """_calculate_weight method is used to calculate weight based on quantity and if quantity is zero and
            per unit weight for the product is not define then weight is zero."""
        quantity = self.product_qty
        per_quantity_weight = self.mo_id.product_tmpl_id.weight
        if quantity and per_quantity_weight:
            self.cr_weight = quantity * per_quantity_weight
            self.mo_id.cr_weight = self.cr_weight
        else:
            self.cr_weight = 0
            self.mo_id.cr_weight = 0

    @api.onchange("cr_weight")
    def _calculate_quantity(self):
        """_calculate_quantity method is used to calculate quantity based on weight and if weight is zero and
            per unit weight for the product is not define then quantity is zero."""
        per_quantity_weight = self.mo_id.product_tmpl_id.weight
        total_weight = self.cr_weight
        if per_quantity_weight:
            if total_weight > 0:
                self.product_qty = total_weight / per_quantity_weight
            else:
                self.product_qty = 0
        else:
            self.product_qty = 0
