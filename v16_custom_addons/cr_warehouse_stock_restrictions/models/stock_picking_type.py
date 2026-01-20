# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    user_id = fields.Many2one(comodel_name="res.users", string="user_id")
    is_restrict_transfer = fields.Boolean(
        string="is_restrict_transfer", compute="_compute_is_restrict_transfer"
    )

    @api.depends("user_id.groups_id")
    def _compute_is_restrict_transfer(self):
        """Compute method that checks if the user belongs to a specific group to apply transfer restrictions"""
        # Reference to the group that restricts transfers
        restrict_group = self.env.ref(
            "cr_warehouse_stock_restrictions.restrict_transfer"
        )

        # Get the current user
        user = self.env.user

        # Check if the user is part of the 'restrict_transfer' group
        if restrict_group and restrict_group in user.groups_id:
            # If the user is in the group, set the field 'is_restrict_transfer' to True
            self.is_restrict_transfer = True
        else:
            # If the user is not in the group, set the field 'is_restrict_transfer' to False
            self.is_restrict_transfer = False
