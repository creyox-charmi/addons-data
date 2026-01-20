from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    cr_task_ids = fields.Many2many(
        "project.task", "cr_task_invoice", "move_id", "task_id", copy=False
    )
