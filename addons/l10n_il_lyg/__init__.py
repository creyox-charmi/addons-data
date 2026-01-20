# -*- coding: utf-8 -*-
# Copyright (C) Gilliam Management Services and Information Systems, Ltd. (the owner of Bizzup), 2021, 2022, 2023, 2024, 2025
# All Rights Reserved to Gilliam Management Services and Information Systems, Ltd.
# Unauthorized copying, editing or printing of this file, in any way is strictly prohibited
# Proprietary and confidential for more information, please contact
# lg@bizzup.app
from . import models
from . import wizard
from odoo import api, SUPERUSER_ID

def post_init(env):
    """Company write"""
    # env = api.Environment(cr, SUPERUSER_ID, {})
    company_id = env.user.company_id.search([('account_fiscal_country_id.code', '=', 'IL')], limit=1)
    if company_id:
        company_id.write({
            'is_l10n_installed': True,
        })
    if company_id and company_id.is_l10n_installed:
        journal_obj = env['account.journal'].search([('type', 'not in', ['bank', 'cash'])])
        for journal in journal_obj:
            journal.update({'restrict_mode_hash_table': True})
