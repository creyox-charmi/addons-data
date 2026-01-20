from odoo import fields, models, api


class Merge(models.TransientModel):
    _name = "cr.merge.invoice"

    cr_merge = fields.Boolean(default=True)
    cr_count_tasks = fields.Integer(
        string="No. of Task",
        default=lambda self: int(
            len(self.env["project.task"].browse(self._context["active_ids"]))
        ),
        readonly=True,
    )

    def check_merge(self):
        """calls the method for creating invoice for selected records"""

        active_ids = self.env["project.task"].browse(self._context["active_ids"])
        active_ids.action_create_invoices(self.cr_merge)
