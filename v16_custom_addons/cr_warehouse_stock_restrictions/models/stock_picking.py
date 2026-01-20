# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, vals):
        print("call")
        """Override the 'create' method to implement custom permission check"""
        # Get the user's group memberships
        user_groups = self.env.user.groups_id

        # Reference to the 'cr_restrict_button' group, which restricts certain actions
        restricted_group = self.env.ref(
            "cr_warehouse_stock_restrictions.cr_restrict_button"
        )

        # Check if the user belongs to the restricted group
        if restricted_group in user_groups:
            # If the user belongs to the restricted group, raise an AccessError to prevent creation
            raise ValidationError(
                _("You do not have permission to create stock picking records.")
            )

        # Call the super method to proceed with the creation of the stock picking record if no restriction applies
        return super(StockPicking, self).create(vals)
