from odoo import models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _visible_menu_ids(self, debug=False):
        visible_ids = super()._visible_menu_ids(debug)
        if self.env.user.has_group('account.group_account_user'):
            accounting_menus = [
                'cr_mm_secret_accounting.menu_custom_accounting_reports',
            ]
            hidden_menu_ids = {self.env.ref(r).sudo().id for r in accounting_menus if self.env.ref(r, raise_if_not_found=False)}
            return visible_ids - hidden_menu_ids
        return visible_ids