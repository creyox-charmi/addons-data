# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import fields, models, api
from odoo.osv import expression
from odoo.tools import Query


class AccountAccount(models.Model):
    _inherit = "account.account"

    secret = fields.Boolean(
        string="Secret",
        help="If checked, this account is hidden for users below Bookkeeper level.",
        default=False,
    )

    @api.model
    def _user_has_low_access(self):
        user = self.env.user
        return not user.has_group("account.group_account_manager")

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        if self._user_has_low_access():
            # Include False OR NULL (important for existing rows)
            domain = expression.AND(
                [
                    domain,
                    expression.OR([[("secret", "=", False)], [("secret", "=", None)]]),
                ]
            )

        return super()._search(domain=domain, offset=offset, limit=limit, order=order)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        if self._user_has_low_access():
            args = expression.AND(
                [
                    args,
                    expression.OR([[("secret", "=", False)], [("secret", "=", None)]]),
                ]
            )
        return super().name_search(name=name, args=args, operator=operator, limit=limit)







