from odoo import models, fields, api


class Project(models.Model):
    _inherit = "project.project"

    cr_client_currency_id = fields.Many2one("res.currency")
    cr_client_hourly_rate = fields.Monetary(string="Client Hourly Rate")
    cr_developer_currency_id = fields.Many2one("res.currency")
    cr_count_no_of_invoices = fields.Integer(
        default=0, compute="compute_count_no_of_invoices"
    )
    cr_count_no_of_bills = fields.Integer(
        default=0, compute="compute_count_no_of_bills"
    )

    def compute_count_no_of_invoices(self):
        self.cr_count_no_of_invoices = len(self.tasks.cr_invoice_ids.ids)

    def compute_count_no_of_bills(self):
        self.cr_count_no_of_bills = len(
            self.tasks.cr_developer_assignees_line.cr_bill_id.ids
        )

    def action_show_invoices(self):
        """Smart button action to show invoice/invoices of the respective project"""
        self.ensure_one()

        action = {
            "type": "ir.actions.act_window",
            "name": "Invoices of the Project",
            "res_model": "account.move",
            "context": {"create": False},
            "view_type": "list",
            "view_mode": "list,form",
            "domain": [("id", "in", self.tasks.cr_invoice_ids.ids)],
        }
        return action

    def action_show_all_bills(self):
        """Smart button action to show bill/bills of the respective project"""
        self.ensure_one()

        action = {
            "type": "ir.actions.act_window",
            "name": "Bills of Assignees",
            "res_model": "account.move",
            "context": {"create": False},
        }
        if len(self.tasks) == 1 and self.cr_developer_assignees_line.cr_bill_id:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.tasks.cr_developer_assignees_line.cr_bill_id.id,
                }
            )
        else:
            action.update(
                {
                    "view_type": "list",
                    "view_mode": "list,form",
                    "domain": [
                        (
                            "id",
                            "in",
                            self.tasks.cr_developer_assignees_line.cr_bill_id.ids,
                        )
                    ],
                }
            )

        return action
