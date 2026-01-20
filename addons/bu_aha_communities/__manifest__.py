# Copyright 2022 Yves Goldberg (Ygol InternetWork)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Bu Aha Communities",
    "summary": """
        Communities management for Habayta needs""",
    "version": "19.0.1.0",
    "license": "Other proprietary",
    "author": "Yves Goldberg (Ygol InternetWork)",
    "website": "https://www.ygol.com",
    "depends": [
        "base",
        "hr",
        "calendar",
        "account",
        "mail",
        "project",
        "hr_expense",
        "base_automation",
    ],  # contacts
    "data": [
        "security/bu_community_security.xml",
        "security/ir.model.access.csv",
        "views/bu_community.xml",
        "views/bu_community_tag.xml",
        "views/hr_employee.xml",
        "views/res_partner.xml",
        "views/calendar_event.xml",
        "views/hr_expense.xml",
        "views/hr_expense_sheet.xml",
        "data/bu_community.xml",
        "report/community_report_templates.xml",
        "report/community_reports.xml",
        "views/calendar_report_views.xml",
    ],
    "demo": [
        # "demo/bu_community.xml",
    ],
    "application": True,
    "installable": True,
}

