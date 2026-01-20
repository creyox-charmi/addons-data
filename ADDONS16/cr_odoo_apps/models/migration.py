# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class Migration(models.Model):
    _name = "cr.migration"
    _description = "Apps Migration"
    _rec_name = "name_id"

    name_id = fields.Many2one("cr.odoo.apps", string="Name", copy=True)
    name = fields.Char(compute="compute_name")
    remarks = fields.Char(string="Remarks")
    assignee_ids = fields.Many2many("res.users", string="Assignees")
    stage_id = fields.Many2one("cr.stage", string="Stage")
    version_id = fields.Many2one("cr.versions.odoo", string="Odoo Versions")
    active = fields.Boolean(default=True)

    @api.onchange("stage_id")
    def stage_on_done(self):
        for record in self:
            if record.stage_id.is_done:
                app = self.env["cr.odoo.apps"].search(
                    [("name", "=", record.name_id.name)], limit=1
                )
                if app:
                    if not record.version_id in app.version_ids:
                        app.write({"version_ids": [(4, record.version_id.id)]})

                    if record.version_id in app.non_migrated_version_ids:
                        app.write(
                            {"non_migrated_version_ids": [(3, record.version_id.id)]}
                        )

                else:
                    raise ValidationError(
                        _("There is no such app available in Odoo Apps")
                    )

    @api.depends("name_id")
    def compute_name(self):
        for rec in self:
            rec.name = rec.name_id.name
