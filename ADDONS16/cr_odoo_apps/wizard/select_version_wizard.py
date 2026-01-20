# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import api, fields, models, _


class CrSelectVersionWizard(models.TransientModel):
    _name = "cr.select.version.wizard"
    _description = "Select Version Wizard"

    version_id = fields.Many2one("cr.versions.odoo", string="Version")

    def action_create_record(self):
        for rec in self:
            selected_version = rec.version_id
            apps = self.env["cr.odoo.apps"].search(
                [("non_migrated_version_ids", "=", selected_version.id)]
            )
            stage_draft = self.env["cr.stage"].search(
                [("is_draft", "=", True)], limit=1
            )

            for app in apps:
                duplicate_rec = self.env["cr.migration"].search(
                    [("name_id", "=", app.id), ("version_id", "=", selected_version.id)]
                )
                if not duplicate_rec:
                    self.env["cr.migration"].create(
                        {
                            "name_id": app.id,
                            "version_id": selected_version.id,
                            "stage_id": stage_draft.id,
                        }
                    )

        action = {
            "type": "ir.actions.act_window",
            "views": [(self.env.ref("cr_odoo_apps.view_tree_migration").id, "tree")],
            "view_mode": "tree",
            "name": _("Migration"),
            "res_model": "cr.migration",
            "target": "main",
        }
        return action
