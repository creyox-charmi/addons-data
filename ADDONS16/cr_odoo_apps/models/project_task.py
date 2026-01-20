from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    odoo_apps_id = fields.Many2one("cr.odoo.apps")

    def move_to_odoo_apps(self):
        return {
            "name": "Move to Odoo Apps Wizard",
            "type": "ir.actions.act_window",
            "res_model": "odoo.app.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("cr_odoo_apps.view_odoo_app_wizard_form").id,
            "target": "new",
            "context": {
                "default_name": self.name,
            },
        }
