{
    'name': 'Hide special accounts and more - MM',
    'version': '18.0',
    'category': 'Accounting',
    'summary': 'Hide special accounts and restrict journal access',
    'author': 'Your Name',
    'depends': ['accountant'],
    "data": [
        "security/ir.model.access.csv",
        'data/partner_ledger.xml',
        'data/aged_receivable_report.xml',
        'data/aged_payable_report.xml',
        "views/account_account_views.xml",
        "views/custom_reports.xml",

    ],
    # "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}