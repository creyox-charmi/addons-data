from odoo import models, fields, api


class Assignees(models.Model):
    _name = "cr.developer.assignees"
    _description = "Task Developers Assignees"

    name = fields.Many2one("res.users", string="Assignees")
    cr_developer_amount = fields.Monetary(
        string="Amount", currency_field="cr_currency_id"
    )
    cr_currency_id = fields.Many2one("res.currency", string="Currency")
    cr_developer_payment_status = fields.Selection(
        string="Payment Status",
        selection=[
            ("not_paid", "Not Paid"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
        ],
        compute="compute_developer_payment_status",
        store=True,
        default="not_paid",
    )
    cr_project_task_id = fields.Many2one("project.task")
    cr_bill_id = fields.Many2one("account.move")
    cr_assignees_analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account for Assignees"
    )
    cr_project_id = fields.Many2one(related="cr_project_task_id.project_id")

    @api.depends("cr_bill_id", "cr_bill_id.payment_state")
    def compute_developer_payment_status(self):
        for developer in self:
            if developer.cr_bill_id.payment_state == "paid":
                developer.cr_developer_payment_status = "paid"

            elif developer.cr_bill_id.payment_state == "partial":
                developer.cr_developer_payment_status = "partial"

            else:
                developer.cr_developer_payment_status = "not_paid"

    @api.onchange("name")
    def _change_name(self):
        self.cr_currency_id = self.cr_project_id.cr_developer_currency_id.id
        self.cr_assignees_analytic_account_id = (
            self.cr_project_id.analytic_account_id.id
        )
