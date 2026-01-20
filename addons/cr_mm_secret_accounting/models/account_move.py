# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import fields, models, api
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv import expression
from odoo import fields, models, api
from odoo.osv import expression
from odoo.http import request as http_request

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

    def _is_aged_report_from_url(self):
        """Check if current request is for an aged report based on URL."""
        try:
            if http_request and hasattr(http_request, 'httprequest'):
                # Check current path
                path = http_request.httprequest.path

                # Also check the referer (where the request came from)
                referer = http_request.httprequest.referrer

                # Check if URL contains aged report paths
                aged_report_paths = [
                    '/odoo/aged-payable-secret',
                    '/odoo/aged-receivable-secret',
                    'aged-payable',
                    'aged-receivable'
                ]

                # Check both current path and referer
                if referer:
                    if any(aged_path in referer for aged_path in aged_report_paths):
                        return True

                return any(aged_path in path for aged_path in aged_report_paths)
        except Exception as e:
            pass

        # Fallback: check context
        return self.env.context.get('secret_report', False)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        if self._user_has_low_access():
            # Check if we're in an aged report by examining the URL
            is_aged_report = self._is_aged_report_from_url()

            if is_aged_report:
                # For aged reports: only exclude moves that are ENTIRELY secret
                self.env.cr.execute(
                    """
                    SELECT am.id
                      FROM account_move am
                     WHERE EXISTS (
                           SELECT 1
                             FROM account_move_line aml
                             JOIN account_account acc ON acc.id = aml.account_id
                            WHERE aml.move_id = am.id
                              AND COALESCE(acc.secret, FALSE) = FALSE
                     )
                """
                )
            else:
                # For other reports: exclude moves with ANY secret line
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

    def check_access_rights(self, operation, raise_exception=True):
        """Override to check secret access when reading moves."""
        res = super().check_access_rights(operation, raise_exception=raise_exception)

        if operation == 'read' and self._user_has_low_access():
            # Check will be done in check_access_rule
            pass

        return res

    def check_access_rule(self, operation):
        """Prevent low-access users from viewing moves with secret lines."""
        res = super().check_access_rule(operation)

        if operation == 'read' and self._user_has_low_access():
            # Check if any of the moves being accessed contain secret lines
            for move in self:
                if move.is_secret:
                    raise AccessError(
                        "You don't have permission to access this journal entry "
                        "because it contains confidential account information."
                    )

        return res

    def read(self, fields=None, load='_classic_read'):
        """Override read to block access to secret moves."""
        if self._user_has_low_access():
            # Filter out secret moves before reading
            accessible_moves = self.filtered(lambda m: not m.is_secret)
            if len(accessible_moves) < len(self):
                # Some moves are secret
                secret_count = len(self) - len(accessible_moves)
                if not accessible_moves:
                    # All moves are secret
                    raise AccessError(
                        "You don't have permission to access this journal entry "
                        "because it contains confidential account information."
                    )
            return super(AccountMove, accessible_moves).read(fields=fields, load=load)

        return super().read(fields=fields, load=load)

    def get_formview_action(self, access_uid=None):
        """Block opening form view for secret moves."""
        if self._user_has_low_access():
            if self.is_secret:
                raise AccessError(
                    "You don't have permission to access this journal entry "
                    "because it contains confidential account information."
                )
        return super().get_formview_action(access_uid=access_uid)