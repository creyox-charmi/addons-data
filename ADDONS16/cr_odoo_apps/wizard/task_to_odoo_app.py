from odoo import models, fields, api


class OdooAppWizard(models.TransientModel):
    _name = "odoo.app.wizard"
    _description = "Odoo App Wizard"

    name = fields.Char(string="App Name", required=True)
    tech_name = fields.Char(string="Technical Name", required=True)
    category_id = fields.Many2one("cr.categories", string="Category", required=True)
    version_ids = fields.Many2many(
        "cr.versions.odoo",
        "wizard_version_app_relation",
        "app_id",
        "version_id",
        string="Available Versions",
    )
    non_migrated_version_ids = fields.Many2many(
        "cr.versions.odoo",
        "wizard_non_available_version_app_relation",
        "app_id",
        "version_id",
        string="Non Migrated Versions",
    )

    @api.model
    def default_get(self, fields):
        defaults = super(OdooAppWizard, self).default_get(fields)

        active_id = self.env.context.get("active_id")

        if active_id:
            record = self.env["project.task"].browse(active_id)
            if record:
                app_record = self.env["cr.odoo.apps"].search(
                    [("id", "=", record.odoo_apps_id.id)], limit=1
                )
                if app_record:
                    defaults.update(
                        {
                            "name": app_record.name,
                            "tech_name": app_record.tech_name,
                            "category_id": app_record.category_id.id,
                            "version_ids": [(6, 0, app_record.version_ids.ids)],
                            "non_migrated_version_ids": [
                                (6, 0, app_record.non_migrated_version_ids.ids)
                            ],
                        }
                    )

        return defaults

    def action_create_app(self):
        active_id = self.env.context.get("active_id")
        record = self.env["project.task"].browse(active_id)
        existing_app = self.env["cr.odoo.apps"].search(
            [("id", "=", record.odoo_apps_id.id)], limit=1
        )
        if not existing_app:
            rec = self.env["cr.odoo.apps"].create(
                {
                    "name": self.name,
                    "tech_name": self.tech_name,
                    "category_id": self.category_id.id,
                    "version_ids": [(6, 0, self.version_ids.ids)],
                    "non_migrated_version_ids": [
                        (6, 0, self.non_migrated_version_ids.ids)
                    ],
                }
            )
            record.write({"odoo_apps_id": rec.id})
        else:
            existing_app.write(
                {
                    "tech_name": self.tech_name,
                    "category_id": self.category_id.id,
                    "version_ids": [(6, 0, self.version_ids.ids)],
                    "non_migrated_version_ids": [
                        (6, 0, self.non_migrated_version_ids.ids)
                    ],
                }
            )
