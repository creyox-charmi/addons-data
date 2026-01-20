# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import fields, models, api
from odoo.osv import expression


class AccountMove(models.Model):
    _inherit = "account.move"

    is_secret = fields.Boolean(
        string="Is Secret",
        compute="_compute_is_secret",
        store=True,  # optional if you want to store the value
    )

    @api.depends("line_ids.account_id.secret")
    def _compute_is_secret(self):
        for move in self:
            move.is_secret = any(move.line_ids.mapped("account_id.secret"))

    @api.model
    def _user_has_low_access(self):
        user = self.env.user
        return not user.has_group("account.group_account_manager")

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        if self._user_has_low_access():
            # Keep only moves that have NO secret lines (secret TRUE) at all.
            # Use COALESCE so NULL is treated as FALSE.
            self.env.cr.execute(
                """
                SELECT am.id
                  FROM account_move am
                 WHERE NOT EXISTS (
                       SELECT 1
                         FROM account_move_line aml
                         JOIN account_account acc ON acc.id = aml.account_id
                        WHERE aml.move_id = am.id
                          AND COALESCE(acc.secret, FALSE) = TRUE
                 )
            """
            )
            allowed_move_ids = [r[0] for r in self.env.cr.fetchall()]

            if not allowed_move_ids:
                return super()._search(
                    [("id", "=", 0)], offset=offset, limit=limit, order=order
                )

            domain = expression.AND([domain, [("id", "in", allowed_move_ids)]])

        return super()._search(domain=domain, offset=offset, limit=limit, order=order)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        if self._user_has_low_access():
            self.env.cr.execute(
                """
                SELECT am.id
                  FROM account_move am
                 WHERE NOT EXISTS (
                       SELECT 1
                         FROM account_move_line aml
                         JOIN account_account acc ON acc.id = aml.account_id
                        WHERE aml.move_id = am.id
                          AND COALESCE(acc.secret, FALSE) = TRUE
                 )
            """
            )
            allowed_move_ids = [r[0] for r in self.env.cr.fetchall()]
            if not allowed_move_ids:
                return []
            args = expression.AND([args, [("id", "in", allowed_move_ids)]])
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
