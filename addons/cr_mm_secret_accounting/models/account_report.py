# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, api
from odoo.osv import expression
from odoo import models, fields, api, _, osv
from odoo.tools import date_utils, get_lang, float_is_zero, float_repr, SQL, parse_version, Query

class AccountReport(models.Model):
    _inherit = "account.report"

    @api.model
    def _get_options_account_type_domain(self, options):
        """Custom logic only for non-privileged users."""
        user = self.env.user
        is_privileged = user.has_group("account.group_account_manager")

        # ✔️ Privileged → Use Odoo base behavior
        if is_privileged:
            return super()._get_options_account_type_domain(options)

        all_domains = []
        selected_domains = []
        if not options.get('account_type') or len(options.get('account_type')) == 0:
            return []
        for opt in options.get('account_type', []):
            if opt['id'] == 'trade_receivable':
                domain = [('account_id.non_trade', '=', False), ('account_id.account_type', '=', 'asset_receivable'),('account_id.secret','=',False)]
            elif opt['id'] == 'trade_payable':
                domain = [('account_id.non_trade', '=', False), ('account_id.account_type', '=', 'liability_payable'),('account_id.secret','=',False)]
            elif opt['id'] == 'non_trade_receivable':
                domain = [('account_id.non_trade', '=', True), ('account_id.account_type', '=', 'asset_receivable'),('account_id.secret','=',False)]
            elif opt['id'] == 'non_trade_payable':
                domain = [('account_id.non_trade', '=', True), ('account_id.account_type', '=', 'liability_payable'),('account_id.secret','=',False)]
            if opt['selected']:
                selected_domains.append(domain)
            all_domains.append(domain)
        return osv.expression.OR(selected_domains or all_domains)


