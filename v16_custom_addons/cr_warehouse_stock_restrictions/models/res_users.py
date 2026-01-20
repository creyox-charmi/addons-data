# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    stock_picking_type_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Default Warehouse Operations",
        require=True,
    )
    is_restrict_locations = fields.Boolean(string="Restrict Location")
    stock_location_ids = fields.Many2many(
        comodel_name="stock.location", string="Stock Locations", require=True
    )
    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse", string="Warehouses", require=True
    )
    limit_sale_order = fields.Integer(string="Limit Sale Order")
    is_limit_sale_order = fields.Boolean(
        string="is_limit_sale_order", compute="_compute_is_limit_sale_order"
    )
    is_restrict_sale_warehouses = fields.Boolean(
        string="is_limit_sale_order", compute="_compute_is_restrict_sale_warehouses"
    )

    @api.depends("groups_id")
    def _compute_is_limit_sale_order(self):
        """Compute method to check if the user belongs to a group that limits sale orders"""
        restrict_group = self.env.ref(
            "cr_warehouse_stock_restrictions.cr_restrict_sale_order_limit"
        )
        # If the user is part of the restrict sale warehouses group, apply restrictions
        if restrict_group and restrict_group in self.groups_id:
            self.set_limit()
            self.is_limit_sale_order = True
        else:
            self.reset_limit()
            self.is_limit_sale_order = False

    @api.depends("groups_id")
    def _compute_is_restrict_sale_warehouses(self):
        """Compute method to check if the user belongs to a group that restricts sale warehouses"""
        restrict_group = self.env.ref(
            "cr_warehouse_stock_restrictions.restrict_sale_warehouses"
        )
        if restrict_group and restrict_group in self.groups_id:
            self.restrict_sale_wh()
            self.is_restrict_sale_warehouses = True
        else:
            self.un_restrict_sale_wh()
            self.is_restrict_sale_warehouses = False

    def set_limit(self):
        """Method to set the sale order limit on stock picking actions"""
        for record in self:
            action_name = ["Deliveries", "Receipts", "All Transfers"]
            actions = record.env["ir.actions.act_window"].search(
                [
                    ("name", "in", action_name),
                    ("res_model", "=", "stock.picking"),
                    ("target", "=", "current"),
                    ("type", "=", "ir.actions.act_window"),
                ]
            )
            if actions:
                for action in actions:
                    action.write({"limit": record.limit_sale_order})

    def reset_limit(self):
        """Method to reset the sale order limit to the default value"""
        for record in self:
            action_name = ["Deliveries", "Receipts", "All Transfers"]
            actions = record.env["ir.actions.act_window"].search(
                [
                    ("name", "in", action_name),
                    ("res_model", "=", "stock.picking"),
                    ("target", "=", "current"),
                    ("type", "=", "ir.actions.act_window"),
                ]
            )
            if actions:
                for action in actions:
                    action.write({"limit": 80})

    def restrict_sale_wh(self):
        """Method to remove sale order warehouse restrictions by setting the limit"""
        for record in self:
            action = record.env["ir.actions.act_window"].search(
                [
                    ("name", "=", "Quotations"),
                    ("res_model", "=", "sale.order"),
                    ("target", "=", "current"),
                    ("type", "=", "ir.actions.act_window"),
                ]
            )
            if action:
                action.write({"limit": record.limit_sale_order})

    def un_restrict_sale_wh(self):
        """Method to remove sale order warehouse restrictions by resetting the limit"""
        for record in self:
            action = record.env["ir.actions.act_window"].search(
                [
                    ("name", "=", "Quotations"),
                    ("res_model", "=", "sale.order"),
                    ("target", "=", "current"),
                    ("type", "=", "ir.actions.act_window"),
                ]
            )
            if action:
                action.write({"limit": 80})
