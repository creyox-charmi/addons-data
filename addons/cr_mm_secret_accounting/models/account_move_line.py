# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import fields, models, api
from odoo.http import request
from odoo.osv import expression
from odoo import fields, models, api
from odoo.osv import expression
from odoo.http import request as http_request

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_secret = fields.Boolean(
        string="Is Secret",
        compute="_compute_is_secret",
        store=True,  # optional if you want to store the value
    )

    @api.depends("account_id.secret")
    def _compute_is_secret(self):
        for move in self:
            move.is_secret = move.account_id.secret

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
                # For aged reports: only hide secret lines
                self.env.cr.execute(
                    """
                    SELECT aml.id
                      FROM account_move_line aml
                      JOIN account_account acc ON acc.id = aml.account_id
                     WHERE COALESCE(acc.secret, FALSE) = FALSE
                """
                )
            else:
                # For other reports: hide lines from moves containing any secret line
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