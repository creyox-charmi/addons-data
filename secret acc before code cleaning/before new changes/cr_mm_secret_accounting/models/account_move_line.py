# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import fields, models, api
from odoo.osv import expression


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _user_has_low_access(self):
        user = self.env.user
        return not user.has_group("account.group_account_manager")

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        if self._user_has_low_access():
            # Lines must use NON-secret accounts (False or NULL) AND belong to moves with NO secret lines.
            self.env.cr.execute(
                """
                SELECT aml.id
                  FROM account_move_line aml
                  JOIN account_account acc ON acc.id = aml.account_id
                 WHERE COALESCE(acc.secret, FALSE) = FALSE
                   AND NOT EXISTS (
                       SELECT 1
                         FROM account_move_line aml2
                         JOIN account_account acc2 ON acc2.id = aml2.account_id
                        WHERE aml2.move_id = aml.move_id
                          AND COALESCE(acc2.secret, FALSE) = TRUE
                   )
            """
            )
            allowed_line_ids = [r[0] for r in self.env.cr.fetchall()]

            if not allowed_line_ids:
                return super()._search(
                    [("id", "=", 0)], offset=offset, limit=limit, order=order
                )

            domain = expression.AND([domain, [("id", "in", allowed_line_ids)]])

        return super()._search(domain=domain, offset=offset, limit=limit, order=order)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        if self._user_has_low_access():
            self.env.cr.execute(
                """
                SELECT aml.id
                  FROM account_move_line aml
                  JOIN account_account acc ON acc.id = aml.account_id
                 WHERE COALESCE(acc.secret, FALSE) = FALSE
                   AND NOT EXISTS (
                       SELECT 1
                         FROM account_move_line aml2
                         JOIN account_account acc2 ON acc2.id = aml2.account_id
                        WHERE aml2.move_id = aml.move_id
                          AND COALESCE(acc2.secret, FALSE) = TRUE
                   )
            """
            )
            allowed_line_ids = [r[0] for r in self.env.cr.fetchall()]
            if not allowed_line_ids:
                return []
            args = expression.AND([args, [("id", "in", allowed_line_ids)]])
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    def _where_calc(self, domain, active_test=True):
        # First build query normally
        query = super()._where_calc(domain, active_test)

        user = self.env.user
        is_privileged = user.has_group("account.group_account_manager")
        if not is_privileged:
            domain = expression.AND([domain, [("move_id.is_secret", "=", False)]])
            query = super(AccountMoveLine, self)._where_calc(domain, active_test)

        # if self.env.context.get("secret_report"):
        #     user = self.env.user
        #     is_privileged = user.has_group(
        #         "account.group_account_user"
        #     ) or user.has_group("account.group_account_manager")
        #     if not is_privileged:
        #         domain = expression.AND([domain, [("move_id.is_secret", "=", False)]])
        #         query = super(AccountMoveLine, self)._where_calc(domain, active_test)

        return query