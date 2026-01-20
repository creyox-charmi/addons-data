# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Odoo Apps Management Tool",
    "author": "Creyox Technologies",
    "version": "16.0.0.0",
    "summary": "This app includes advanced customizations for managing the status of Odoo apps within the ERP.",
    "sequence": 9,
    "description": """This app includes advanced customizations for managing the status of Odoo apps within the ERP""",
    "category": "Extra Tools",
    "website": "www.creyox.com",
    "depends": ["base", "project"],
    "data": [
        "security/ir.model.access.csv",
        "views/migration.xml",
        "views/odoo_apps.xml",
        "views/stage.xml",
        "views/version.xml",
        "views/category.xml",
        "views/project_task.xml",
        "wizard/select_version_wizard.xml",
        "wizard/task_to_odoo_app.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "/cr_odoo_apps/static/src/migration_views.js",
            "/cr_odoo_apps/static/src/migration_model.js",
            "/cr_odoo_apps/static/src/migration_controller.js",
            "/cr_odoo_apps/static/src/migration_button.xml",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
