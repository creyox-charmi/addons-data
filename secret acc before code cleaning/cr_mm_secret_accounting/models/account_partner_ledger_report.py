from odoo import api, models, _, fields
import logging

_logger = logging.getLogger(__name__)
class AccountPartnerLedgerCustom(models.AbstractModel):
    _inherit = "account.partner.ledger.report.handler"



    # def _get_query_sums(self, options) -> SQL:
    #     """Override sums to exclude secret accounts for non-privileged users."""
    #     queries = []
    #     report = self.env.ref('account_reports.partner_ledger_report')
    #
    #     user = self.env.user
    #     is_privileged = user.has_group("account.group_account_user") or user.has_group("account.group_account_manager")
    #
    #     for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
    #         column_group_options = column_group_options.copy()
    #
    #         # Inject secret account filter for non-privileged users
    #         if not is_privileged:
    #             forced_domain = column_group_options.get("forced_domain", [])
    #             forced_domain.append(("account_id.secret", "!=", True))
    #             column_group_options["forced_domain"] = forced_domain
    #
    #         query = report._get_report_query(column_group_options, 'from_beginning')
    #
    #         sql_query = SQL(
    #             """
    #             SELECT
    #                 account_move_line.partner_id AS groupby,
    #                 %(column_group_key)s AS column_group_key,
    #                 SUM(%(debit_select)s) AS debit,
    #                 SUM(%(credit_select)s) AS credit,
    #                 SUM(%(balance_select)s) AS amount,
    #                 SUM(%(balance_select)s) AS balance
    #             FROM %(table_references)s
    #             %(currency_table_join)s
    #             WHERE %(search_condition)s
    #             GROUP BY account_move_line.partner_id
    #             """,
    #             column_group_key=column_group_key,
    #             debit_select=report._currency_table_apply_rate(SQL("account_move_line.debit")),
    #             credit_select=report._currency_table_apply_rate(SQL("account_move_line.credit")),
    #             balance_select=report._currency_table_apply_rate(SQL("account_move_line.balance")),
    #             table_references=query.from_clause,
    #             currency_table_join=report._currency_table_aml_join(column_group_options),
    #             search_condition=query.where_clause,
    #         )
    #
    #         _logger.info("Partner Ledger SQL for column group %s:\n%s", column_group_key,
    #                      self._cr.mogrify(sql_query).decode())
    #         queries.append(sql_query)
    #
    #     final_query = SQL(' UNION ALL ').join(queries)
    #     _logger.info("Final Partner Ledger SQL (all column groups):\n%s", self._cr.mogrify(final_query).decode())
    #     return final_query

    # def _get_aml_values(self, options, partner_ids=None, offset=0, limit=None):
    #     rslt = super()._get_aml_values(options, partner_ids, offset=offset, limit=limit)
    #
    #     user = self.env.user
    #     is_privileged = (
    #             user.has_group("account.group_account_user")
    #             or user.has_group("account.group_account_manager")
    #     )
    #
    #     print("DEBUG: Original rslt from super():", rslt)
    #     print("DEBUG: Current user:", user.name, "ID:", user.id)
    #     print("DEBUG: User is privileged:", is_privileged)
    #
    #     if is_privileged:
    #         return rslt  # privileged users see all
    #
    #     # Prefetch all account_ids from AMLs
    #     account_ids = list({aml['account_id'] for aml_list in rslt.values() for aml in aml_list})
    #     print("DEBUG: account_ids collected from AMLs:", account_ids)
    #
    #     # Fetch secret accounts via SQL
    #     self.env.cr.execute("""
    #         SELECT id
    #         FROM account_account
    #         WHERE id = ANY(%s) AND COALESCE(secret, FALSE) = TRUE
    #     """, (account_ids,))
    #     secret_account_ids = {row[0] for row in self.env.cr.fetchall()}
    #     print("DEBUG: secret_account_ids (from AML accounts):", secret_account_ids)
    #
    #     filtered_rslt = {}
    #
    #     for partner_id, aml_list in rslt.items():
    #         filtered_amls = []
    #         print(f"\nDEBUG: Processing Partner {partner_id}, total AMLs: {len(aml_list)}")
    #
    #         for aml in aml_list:
    #             aml_id = aml['id']
    #             aml_account_id = aml['account_id']
    #             move_name = aml['move_name']
    #
    #             print("DEBUG: Checking AML ID:", aml_id, "Account ID:", aml_account_id, "Move:", move_name)
    #
    #             # Skip if AML account is secret
    #             if aml_account_id in secret_account_ids:
    #                 print(f"DEBUG: Skipping AML {aml_id} → AML account {aml_account_id} is secret")
    #                 continue
    #
    #             # SQL: Check if any account.move.line of this AML's parent move has a secret account
    #             self.env.cr.execute("""
    #                 SELECT 1
    #                 FROM account_move_line aml
    #                 JOIN account_account acc ON aml.account_id = acc.id
    #                 JOIN account_move m ON aml.move_id = m.id
    #                 WHERE m.name = %s
    #                   AND COALESCE(acc.secret, FALSE) = TRUE
    #                 LIMIT 1
    #             """, (move_name,))
    #             secret_line_exists = self.env.cr.fetchone()
    #             print(f"DEBUG: Secret line in move {move_name} exists?:", secret_line_exists)
    #
    #             if secret_line_exists:
    #                 print(f"DEBUG: Skipping AML {aml_id} → secret line found in parent move")
    #                 continue
    #
    #             print(f"DEBUG: AML {aml_id} passed all secret checks → keeping it")
    #             filtered_amls.append(aml)
    #
    #         filtered_rslt[partner_id] = filtered_amls
    #         print(f"DEBUG: Partner {partner_id} AML count after filter: {len(filtered_amls)}")
    #
    #     print("DEBUG: Filtering complete. Result:", filtered_rslt)
    #     return filtered_rslt


# -*- coding: utf-8 -*-
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


# ------------------------------
# Helper Mixin to filter secret accounts
# ------------------------------
class AccountReportSecretMixin(models.AbstractModel):
    _name = "account.report.secret.mixin"

    # def _filter_secret_amls(self, amls_by_partner):
    #     """Filter out secret account lines for non-privileged users"""
    #     user = self.env.user
    #     # Privileged users: Bookkeeper & Administrator
    #     if user.has_group("account.group_account_user") or user.has_group("account.group_account_manager"):
    #         return amls_by_partner
    #
    #     # Collect all account_ids
    #     account_ids = list({aml['account_id'] for aml_list in amls_by_partner.values() for aml in aml_list})
    #     if not account_ids:
    #         return amls_by_partner
    #
    #     self.env.cr.execute("""
    #         SELECT id FROM account_account
    #         WHERE id = ANY(%s) AND COALESCE(secret, FALSE) = TRUE
    #     """, (account_ids,))
    #     secret_account_ids = {row[0] for row in self.env.cr.fetchall()}
    #
    #     filtered_rslt = {}
    #     for partner_id, aml_list in amls_by_partner.items():
    #         filtered_amls = []
    #         for aml in aml_list:
    #             if aml['account_id'] in secret_account_ids:
    #                 continue
    #             # Check if any line in the move is secret
    #             self.env.cr.execute("""
    #                 SELECT 1
    #                 FROM account_move_line aml
    #                 JOIN account_account acc ON aml.account_id = acc.id
    #                 JOIN account_move m ON aml.move_id = m.id
    #                 WHERE m.name = %s
    #                   AND COALESCE(acc.secret, FALSE) = TRUE
    #                 LIMIT 1
    #             """, (aml['move_name'],))
    #             if self.env.cr.fetchone():
    #                 continue
    #             filtered_amls.append(aml)
    #         filtered_rslt[partner_id] = filtered_amls
    #     return filtered_rslt


# ------------------------------
# Partner Ledger Custom Report
# ------------------------------
class PartnerLedgerCustom(models.AbstractModel):
    _name = "account.partner.ledger.custom"
    _description = "Partner Ledger (Custom)"
    _inherit = "account.partner.ledger.report.handler"

    # def _get_report_query(self, options, expanded_account=None, fetch_lines=True):
    #     # get the base query
    #     query, params = super()._get_report_query(options, expanded_account, fetch_lines)
    #
    #     user = self.env.user
    #     is_privileged = (
    #             user.has_group("account.group_account_user")
    #             or user.has_group("account.group_account_manager")
    #     )
    #     if not is_privileged:
    #         # inject filter so only non-secret moves appear
    #         query = expression.AND([
    #             query,
    #             [('move_id.is_secret', '=', False)]
    #         ])
    #
    #     return query, params

    # def _get_aml_values(self, options, partner_ids=None, offset=0, limit=None):
    #     aml_values = super()._get_aml_values(options, partner_ids, offset=offset, limit=limit)
    #     return self.env["account.report.secret.mixin"]._filter_secret_amls(aml_values)

    # def _get_aml_values(self, options, partner_ids=None, offset=0, limit=None):
    #     rslt = super()._get_aml_values(options, partner_ids, offset=offset, limit=limit)
    #
    #     user = self.env.user
    #     is_privileged = (
    #             user.has_group("account.group_account_user")
    #             or user.has_group("account.group_account_manager")
    #     )
    #
    #     print("DEBUG: Original rslt from super():", rslt)
    #     print("DEBUG: Current user:", user.name, "ID:", user.id)
    #     print("DEBUG: User is privileged:", is_privileged)
    #
    #     if is_privileged:
    #         return rslt  # privileged users see all
    #
    #     # Prefetch all account_ids from AMLs
    #     account_ids = list({aml['account_id'] for aml_list in rslt.values() for aml in aml_list})
    #     print("DEBUG: account_ids collected from AMLs:", account_ids)
    #
    #     # Fetch secret accounts via SQL
    #     self.env.cr.execute("""
    #         SELECT id
    #         FROM account_account
    #         WHERE id = ANY(%s) AND COALESCE(secret, FALSE) = TRUE
    #     """, (account_ids,))
    #     secret_account_ids = {row[0] for row in self.env.cr.fetchall()}
    #     print("DEBUG: secret_account_ids (from AML accounts):", secret_account_ids)
    #
    #     filtered_rslt = {}
    #
    #     for partner_id, aml_list in rslt.items():
    #         filtered_amls = []
    #         print(f"\nDEBUG: Processing Partner {partner_id}, total AMLs: {len(aml_list)}")
    #
    #         for aml in aml_list:
    #             aml_id = aml['id']
    #             aml_account_id = aml['account_id']
    #             move_name = aml['move_name']
    #
    #             print("DEBUG: Checking AML ID:", aml_id, "Account ID:", aml_account_id, "Move:", move_name)
    #
    #             # Skip if AML account is secret
    #             if aml_account_id in secret_account_ids:
    #                 print(f"DEBUG: Skipping AML {aml_id} → AML account {aml_account_id} is secret")
    #                 continue
    #
    #             # SQL: Check if any account.move.line of this AML's parent move has a secret account
    #             self.env.cr.execute("""
    #                 SELECT 1
    #                 FROM account_move_line aml
    #                 JOIN account_account acc ON aml.account_id = acc.id
    #                 JOIN account_move m ON aml.move_id = m.id
    #                 WHERE m.name = %s
    #                   AND COALESCE(acc.secret, FALSE) = TRUE
    #                 LIMIT 1
    #             """, (move_name,))
    #             secret_line_exists = self.env.cr.fetchone()
    #             print(f"DEBUG: Secret line in move {move_name} exists?:", secret_line_exists)
    #
    #             if secret_line_exists:
    #                 print(f"DEBUG: Skipping AML {aml_id} → secret line found in parent move")
    #                 continue
    #
    #             print(f"DEBUG: AML {aml_id} passed all secret checks → keeping it")
    #             filtered_amls.append(aml)
    #
    #         filtered_rslt[partner_id] = filtered_amls
    #         print(f"DEBUG: Partner {partner_id} AML count after filter: {len(filtered_amls)}")
    #
    #     print("DEBUG: Filtering complete. Result:", filtered_rslt)
    #     return filtered_rslt







