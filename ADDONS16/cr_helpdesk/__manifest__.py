# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    "name": "Creyox Support Portal",
    "author": "Creyox Technologies",
    "version": "16.0.0.0",
    "summary": "This module contains customization related to the support portal.",
    "sequence": 10,
    "description": """Support Portal""",
    "category": "Extra Tools",
    "website": "www.creyox.com",
    "depends": ["base", "hr", "website", "cr_odoo_apps"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence_data.xml",
        "data/ticket_generated_email_template.xml",
        "data/internal_notification_email_template.xml",
        "views/support_ticket.xml",
        "views/cr_helpdesk_view.xml",
        "views/cr_helpdesk_submit.xml",
        "views/helpdesk_stage_view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
    "assets": {
        "web.assets_frontend": [
            "cr_helpdesk/static/src/**/*",
            "https://www.google.com/recaptcha/api.js",
        ],
    },
}
