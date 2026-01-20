# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    "name": "Hide special accounts and more - MM",
    "version": "18.0.0.6",
    "summary": "Hide special accounts and restrict journal access",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Accounting",
    "depends": ["accountant", "account_reports"],
    "data": [
        "security/ir.model.access.csv",
        "data/partner_ledger.xml",
        "data/aged_receivable_report.xml",
        "data/aged_payable_report.xml",
        "views/account_account_views.xml",
        "views/account_move.xml",
        "views/custom_reports.xml",
    ],
    "license": "OPL-1",
    "installable": True,
    "application": False,
}
