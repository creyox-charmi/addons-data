# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_add_from_catalog(self):
        action = super().action_add_from_catalog()

        if self.company_id.show_catalog_tree_view:
            action['view_mode'] = 'list,kanban'
            tree_view = self.env.ref('cr_show_catalog_as_tree.product_product_tree_view_catalog', raise_if_not_found=False)
            if tree_view:
                action['views'] = [(tree_view.id, 'list'), (False, 'kanban')]

        return action

    def catalog_increase_qty(self, product_id):
        self.ensure_one()
        product = self.env['product.product'].browse(product_id)

        existing_line = self.order_line.filtered(
            lambda line: line.product_id == product and not line.display_type
        )

        if existing_line:
            existing_line[0].product_uom_qty += 1
        else:
            vals = {
                'order_id': self.id,
                'product_id': product_id,
                'product_uom_qty': 1,
            }
            self.env['sale.order.line'].create(vals)

        # Return the updated quantity
        updated_line = self.order_line.filtered(
            lambda line: line.product_id == product and not line.display_type
        )
        return updated_line[0].product_uom_qty if updated_line else 1

    def catalog_decrease_qty(self, product_id):
        self.ensure_one()
        product = self.env['product.product'].browse(product_id)

        existing_line = self.order_line.filtered(
            lambda line: line.product_id == product and not line.display_type
        )

        if existing_line and existing_line[0].product_uom_qty > 0:
            new_qty = existing_line[0].product_uom_qty - 1
            if new_qty > 0:
                existing_line[0].product_uom_qty = new_qty
                return new_qty
            else:
                existing_line[0].unlink()
                return 0

        return 0

    def catalog_remove_product(self, product_id):
        self.ensure_one()
        product = self.env['product.product'].browse(product_id)

        existing_line = self.order_line.filtered(
            lambda line: line.product_id == product and not line.display_type
        )

        if existing_line:
            existing_line[0].unlink()

        return 0

    def catalog_set_qty(self, product_id, quantity):
        self.ensure_one()

        if quantity <= 0:
            return self.catalog_remove_product(product_id)

        product = self.env['product.product'].browse(product_id)

        existing_line = self.order_line.filtered(
            lambda line: line.product_id == product and not line.display_type
        )

        if existing_line:
            existing_line[0].product_uom_qty = quantity
            return quantity
        else:
            vals = {
                'order_id': self.id,
                'product_id': product_id,
                'product_uom_qty': quantity,
            }
            self.env['sale.order.line'].create(vals)
            return quantity