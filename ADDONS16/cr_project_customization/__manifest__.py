# -*- coding: utf-8 -*-
# Part of Creyox technologies.

{
    "name": "Project Customization",
    "summary": """Project Customization""",
    "description": """Project Customization""",
    "category": "Project",
    "author": "Creyox Technologies",
    "website": "https://creyox.com",
    "depends": ["base", "project", "hr_timesheet",],
    "vesion": "16.0",
    "currency": "USD",
    "license": "AGPL-3",
    "images": [],
    "data": [
        "security/ir.model.access.csv",
        "wizard/project_task_invoice_wizard_view.xml",
        "views/project_project_view.xml",
        "views/project_task_view.xml",
        "views/account_analytic_line_view.xml",
        "views/account_move_view.xml",
        "views/project_task_type_view.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
