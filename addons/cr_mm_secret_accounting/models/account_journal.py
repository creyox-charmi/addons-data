# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, api, _
from odoo.exceptions import AccessError

BOOKKEEPER_GROUP = "account.group_account_manager"

class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _is_below_bookkeeper(self):
        # block everyone except superuser and Bookkeepers+
        return (not self.env.su) and (not self.env.user.has_group(BOOKKEEPER_GROUP))

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        # gets called whenever a view for account.journal is loaded (form/tree/search/kanban)
        if self._is_below_bookkeeper() and view_type in {"form", "tree", "kanban", "search"}:
            raise AccessError(_("You don't have permission to access Journal Configuration."))
        return super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

    def get_formview_action(self, access_uid=None):
        # called when the client tries to open a specific journal record
        if self._is_below_bookkeeper():
            raise AccessError(_("You don't have permission to access Journal Configuration."))
        return super().get_formview_action(access_uid=access_uid)