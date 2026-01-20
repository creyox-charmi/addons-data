#############################################################################
# Copyright (C) 2021 Yves Goldberg - Ygol InternetWork - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
##############################################################################

{
    'name': 'Donation link',
    'version': '19.0.0.0',
    'category': 'Localization',
    'summary': """This is the latest basic Israelian localisation necessary to run Odoo in Israel""",
    'description': """
This is the latest basic Israelian localisation necessary to run Odoo in Israel:
================================================================================

This module consists of:
 - Generic Israelian chart of accounts
 - Israelian taxes and tax report
 - Fiscal positions for retention / Palestina
 """,
    "license": "Other proprietary",
    "author": "Yves Goldberg (Ygol InternetWork)",
    "website": "http://www.ygol.com",
    'depends': ["website_links",'website_payment','lyg_receipt','bu_aha_communities','payment'],
    'data': [
        'views/snippets/donation.xml',
        'views/receipt_views.xml',
        'views/utm_campaign_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'donation_habayta/static/src/js/donationnow_click.js',
            'donation_habayta/static/src/js/website_payment_form.js',
        ],
    },
    'auto_install': False,
}