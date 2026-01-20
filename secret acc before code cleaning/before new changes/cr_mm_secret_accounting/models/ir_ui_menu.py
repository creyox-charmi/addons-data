# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _visible_menu_ids(self, debug=False):
        visible_ids = super()._visible_menu_ids(debug)

        # Hide custom accounting reports menu for Bookkeeper and above
        if self.env.user.has_group("account.group_account_manager"):
            accounting_menus = [
                "cr_mm_secret_accounting.menu_custom_accounting_reports"
            ]
            hidden_menu_ids = {
                self.env.ref(r).sudo().id
                for r in accounting_menus
                if self.env.ref(r, raise_if_not_found=False)
            }
            visible_ids -= hidden_menu_ids



        # Hide Partner Ledger, Aged Receivable, Aged Payable for Readonly users only
        # if self.env.user.has_group("account.group_account_readonly") and not self.env.user.has_group(
        #         "account.group_account_user"):
        #
        #     readonly_menus = ["account.account_reports_partners_reports_menu"]
        #
        #     hidden_menu_ids = {
        #         self.env.ref(r).sudo().id
        #         for r in readonly_menus
        #         if self.env.ref(r, raise_if_not_found=False)
        #     }
        #     visible_ids -= hidden_menu_ids
        #
        # return visible_ids

        if (
                self.env.user.has_group("account.group_account_readonly")
                or (
                        self.env.user.has_group("account.group_account_user")
                        and not self.env.user.has_group("account.group_account_manager")
                )
        ) and not self.env.user.has_group("base.group_system"):
            readonly_menus = ["account.account_reports_partners_reports_menu"]

            hidden_menu_ids = {
                self.env.ref(r).sudo().id
                for r in readonly_menus
                if self.env.ref(r, raise_if_not_found=False)
            }
            visible_ids -= hidden_menu_ids

        return visible_ids

