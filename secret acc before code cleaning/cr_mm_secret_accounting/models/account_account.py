from odoo import fields, models, api

# ------------------------------------------------------------
# account.account
# ------------------------------------------------------------
class AccountAccount(models.Model):
    _inherit = 'account.account'

    secret = fields.Boolean(
        string='Secret',
        help='If checked, this account is hidden for users below Bookkeeper level.',
        default=False,
    )

    @api.model
    def _user_has_low_access(self):
        user = self.env.user
        return not (user.has_group('account.group_account_user') or
                    user.has_group('account.group_account_manager'))

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        print("\n>>> _search: account.account")
        print("    domain (before):", domain)
        if self._user_has_low_access():
            # Include False OR NULL (important for existing rows)
            domain = expression.AND([domain, expression.OR([
                [('secret', '=', False)],
                [('secret', '=', None)],
            ])])
            print("    domain (after) :", domain)
        return super()._search(domain=domain, offset=offset, limit=limit, order=order)

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None):
    #     print(">>> _search: account.account")
    #     print("Domain before:", domain)
    #
    #     if self._user_has_low_access():
    #         # Check if domain already has 'id in [...]'
    #         id_in_domain = None
    #         new_domain = []
    #         for d in domain:
    #             if isinstance(d, tuple) and d[0] == 'id' and d[1] == 'in':
    #                 id_in_domain = d[2]
    #             else:
    #                 new_domain.append(d)
    #
    #         if id_in_domain:
    #             # Only allow non-secret accounts
    #             self.env.cr.execute("""
    #                    SELECT id FROM account_account
    #                    WHERE id = ANY(%s) AND secret = FALSE
    #                """, (id_in_domain,))
    #             allowed_ids = [row[0] for row in self.env.cr.fetchall()]
    #             if allowed_ids:
    #                 new_domain.append(('id', 'in', allowed_ids))
    #             else:
    #                 # If no allowed accounts, replace with empty domain
    #                 print("No allowed accounts, returning empty search")
    #                 return self.browse()._search([('id', '=', 0)])
    #         else:
    #             # General search → add secret=False
    #             new_domain.append(('secret', '=', False))
    #
    #         domain = new_domain
    #
    #     print("Domain after:", domain)
    #     return super(AccountAccount, self)._search(domain=domain, offset=offset, limit=limit, order=order)

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None):
    #     """Overriding the _search method to modify how products are searched"""
    #     if self._user_has_low_access():
    #         domain = domain + [("secret", "=", False)]
    #     else:
    #         print(">>> User is not low access → no extra filter")
    #
    #     # Call the original _search method with the modified arguments
    #     return super()._search(domain=domain, offset=offset, limit=limit, order=order)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        print(">>> name_search: account.account")
        args = args or []
        if self._user_has_low_access():
            args = expression.AND([args, expression.OR([
                [('secret', '=', False)],
                [('secret', '=', None)],
            ])])
        return super().name_search(name=name, args=args, operator=operator, limit=limit)





# models/account_report.py
from odoo import models
from odoo.osv import expression
from odoo.osv.expression import SQL
import logging

_logger = logging.getLogger(__name__)

class AccountReport(models.Model):
    _inherit = "account.report"

    # def _get_report_query(self, options, date_scope, domain=None):
    #     """
    #     Generate a Query object filtered for secret accounts for non-privileged users,
    #     adding the secret condition only once.
    #     """
    #     domain = self._get_options_domain(options, date_scope) + (domain or [])
    #
    #     user = self.env.user
    #     secret_condition = ('account_id.secret', '!=', True)
    #     # secret_condition = ('is_secret', '!=', True)
    #
    #     # Only append if not already present and user is not privileged
    #     if not user.has_group("account.group_account_user") and not user.has_group("account.group_account_manager"):
    #         if secret_condition not in domain:
    #             domain.append(secret_condition)
    #
    #     query = self.env['account.move.line']._where_calc(domain)
    #     self.env['account.move.line']._apply_ir_rules(query)
    #     return query

    # def _get_report_query(self, options, date_scope, domain=None):
    #     """
    #     Return the prepared SQL query object for the report.
    #     """
    #     query, params = self._get_query_sums(options)
    #     self._cr.execute(query, params)
    #     return self._cr.fetchall()


class AccountFiscalYear(models.Model):
    _inherit = 'account.fiscal.year'


class AccountReportLine(models.Model):
    _inherit = 'account.report.line'

class AccountReportColumn(models.Model):
    _inherit = "account.report.column"

class AccountGroup(models.Model):
    _inherit = "account.group"

class AccountReportExpression(models.Model):
    _inherit = "account.report.expression"






