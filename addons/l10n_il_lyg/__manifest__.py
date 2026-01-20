# -*- coding: utf-8 -*-
# Copyright (C) Gilliam Management Services and Information Systems, Ltd. (the owner of Bizzup), 2021, 2022, 2023, 2024, 2025
# All Rights Reserved to Gilliam Management Services and Information Systems, Ltd.
# Unauthorized copying, editing or printing of this file, in any way is strictly prohibited
# Proprietary and confidential for more information, please contact
# lg@bizzup.app

{
    'name': 'LYG Israel - Accounting',
    "version": "19.0.1.0.0",
    'category': 'Localization',
    'summary': """This is the latest basic Israelian localisation necessary to run Odoo in Israel""",
    'description': """
This is the latest basic Israeli localisation necessary to run Odoo in Israel:
================================================================================

This module consists of:
 - Generic Israeli chart of accounts
 - Israeli taxes and tax report
 - Fiscal positions for retention / Palestina]
 """,
    "license": "Other proprietary",
    "author": "Yves Goldberg (Ygol InternetWork)",
    "website": "http://www.ygol.com",
    'depends': ['l10n_il', 'partner_bank_code','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'data/ita_branch_list.xml',
        'data/l10n_il_tax_reason_data.xml',
        'data/res_bank.xml',
        'views/account_tax_views.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'views/report_invoice.xml',
        'views/account_journal_view.xml',
    ],
    'auto_install': True,
    'post_init_hook': 'post_init',
}
