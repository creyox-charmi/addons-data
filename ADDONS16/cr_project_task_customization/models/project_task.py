from odoo import fields, models, api
from datetime import date
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    cr_client_hourly_rate = fields.Monetary(
        related="project_id.cr_client_hourly_rate",
        currency_field="cr_client_currency_id",
        readonly=True,
    )
    cr_client_currency_id = fields.Many2one(
        related="project_id.cr_client_currency_id", string="Client Currency"
    )
    cr_approved_hours = fields.Float(
        string="Approved Hours", compute="compute_cr_approved_hours", readonly=False
    )
    cr_total_amount = fields.Monetary(
        string="Total Amount",
        compute="compute_total_amount",
        store=True,
        currency_field="cr_client_currency_id",
        readonly=False,
    )
    cr_task_payment_status = fields.Selection(
        selection=[
            ("not_paid", "Unpaid"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
        ],
        compute="compute_task_payment_status",
        default="not_paid",
        string="Task Payment Status",
    )
    cr_developer_assignees_line = fields.One2many(
        "cr.developer.assignees", "cr_project_task_id"
    )
    cr_invoice_ids = fields.Many2many(
        "account.move", "cr_task_invoice", "task_id", "move_id", copy=False
    )
    cr_count_no_of_bills = fields.Integer(
        default=0, compute="compute_count_no_of_bills"
    )
    cr_count_no_of_invoices = fields.Integer(
        default=0, compute="compute_count_no_of_invoices"
    )
    user_ids = fields.Many2many(
        "res.users",
        relation="project_task_user_rel",
        column1="task_id",
        column2="user_id",
        string="Assignees",
        context={"active_test": False},
        tracking=True,
    )

    @api.depends("cr_total_amount", "cr_client_hourly_rate")
    def compute_cr_approved_hours(self):
        for task in self:
            if task.cr_client_hourly_rate != 0:
                task.cr_approved_hours = (
                    task.cr_total_amount / task.cr_client_hourly_rate
                )

    @api.depends("cr_approved_hours", "cr_client_hourly_rate")
    def compute_total_amount(self):

        for task in self:
            task.cr_total_amount = task.cr_approved_hours * task.cr_client_hourly_rate

    def compute_task_payment_status(self):
        for task in self:

            if not task.cr_invoice_ids:
                task.cr_task_payment_status = "not_paid"

            elif (
                task.cr_invoice_ids
                and task.cr_invoice_ids[0].payment_state == "partial"
            ):
                task.cr_task_payment_status = "partial"

            elif task.cr_invoice_ids and task.cr_invoice_ids[0].payment_state == "paid":
                task.cr_task_payment_status = "paid"

            else:
                task.cr_task_payment_status = "not_paid"

    def compute_count_no_of_bills(self):
        count = 0
        for dev in self.cr_developer_assignees_line:
            if dev.cr_bill_id:
                count += 1
        self.cr_count_no_of_bills = count

    def compute_count_no_of_invoices(self):
        self.cr_count_no_of_invoices = len(self.cr_invoice_ids)

    def create_bill(self):
        """Create Bills of developers in assignees line while clicking
        on "Create Bill" button in form view of this model"""

        if not self.cr_developer_assignees_line:
            raise ValidationError(
                ("You need assign a developer in order to create a bill")
            )
        else:
            for developer in self.cr_developer_assignees_line:

                if not developer.cr_bill_id:
                    new_bill = self.env["account.move"].create(
                        {
                            "partner_id": developer.name.partner_id.id,
                            "ref": self.name,
                            "invoice_date": date.today(),
                            "date": date.today(),
                            "currency_id": self.project_id.cr_developer_currency_id.id,
                            "move_type": "in_invoice",
                            "invoice_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "name": self.name,
                                        "quantity": 1,
                                        "analytic_distribution": {
                                            developer.cr_assignees_analytic_account_id.id: 100
                                        },
                                        "price_unit": developer.cr_developer_amount,
                                        "tax_ids": False,
                                    },
                                )
                            ],
                        }
                    )

                    developer.cr_bill_id = new_bill.id

    def create_invoice(self):
        """Create Invoice of Customer while clicking
        on "Create Invoice" button in form view of this model"""

        uom = self.env["uom.uom"].search([("name", "=", "Hours")], limit=1)
        odoo_product = self.env["product.product"].search(
            [("cr_odoo_service", "=", True)], limit=1
        )

        if not self.cr_invoice_ids:
            if self.cr_approved_hours == 0:
                raise ValidationError(
                    ("Cannot create an invoice of 'zero' Approved Hours")
                )

            new_invoice = self.env["account.move"].create(
                {
                    "partner_id": self.project_id.partner_id.id,
                    "payment_reference": self.name,
                    "invoice_date": date.today(),
                    "currency_id": self.project_id.cr_client_currency_id.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": odoo_product.id,
                                "name": self.name,
                                "quantity": self.cr_approved_hours,
                                "product_uom_id": uom.id,
                                "analytic_distribution": {
                                    self.project_id.analytic_account_id.id: 100
                                },
                                "price_unit": self.cr_client_hourly_rate,
                                "tax_ids": False,
                            },
                        )
                    ],
                }
            )
            self.write({"cr_invoice_ids": [(4, new_invoice.id)]})

        else:
            confirmed_invoice_qty_hours = 0
            for invoice_id in self.cr_invoice_ids:
                if invoice_id.state == "posted":
                    for invoice_line in invoice_id.invoice_line_ids:
                        if invoice_line.name == self.name:
                            confirmed_invoice_qty_hours += invoice_line.quantity

            if confirmed_invoice_qty_hours < self.cr_approved_hours:
                new_invoice = self.env["account.move"].create(
                    {
                        "partner_id": self.project_id.partner_id.id,
                        "payment_reference": self.name,
                        "invoice_date": date.today(),
                        "currency_id": self.project_id.cr_client_currency_id.id,
                        "move_type": "out_invoice",
                        "invoice_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": odoo_product.id,
                                    "name": self.name,
                                    "quantity": self.cr_approved_hours
                                    - confirmed_invoice_qty_hours,
                                    "product_uom_id": uom.id,
                                    "analytic_distribution": {
                                        self.project_id.analytic_account_id.id: 100
                                    },
                                    "price_unit": self.cr_client_hourly_rate,
                                    "tax_ids": False,
                                },
                            )
                        ],
                    }
                )
                self.write({"cr_invoice_ids": [(4, new_invoice.id)]})

    def action_create_bills(self, merge):
        """Create merge/separate bills for developer assignees of selected record from 'Action' in tree view of this model"""

        odoo_product = self.env["product.product"].search(
            [("cr_odoo_service", "=", True)], limit=1
        )

        if merge:
            bills = self.env["account.move"]
            user_wise_task = {}
            for task in self:
                for dev in task.cr_developer_assignees_line:
                    if not dev.cr_bill_id:
                        if dev.name not in user_wise_task:
                            user_wise_task[dev.name] = []
                        user_wise_task[dev.name].append(task)

            for user, tasks in user_wise_task.items():
                bill_lines = []
                for task in tasks:
                    dev = task.cr_developer_assignees_line.filtered(
                        lambda line: line.name == user and not line.cr_bill_id
                    )
                    bill_line_data = {
                        "product_id": odoo_product.id,
                        "name": task.name,
                        "analytic_distribution": {
                            task.project_id.analytic_account_id.id: 100.0
                        },
                        "quantity": 1,
                        "price_unit": dev.cr_developer_amount,
                        "tax_ids": False,
                    }

                    bill_lines.append((0, 0, bill_line_data))

                bill = self.env["account.move"].create(
                    {
                        "move_type": "in_invoice",
                        "invoice_date": date.today(),
                        "currency_id": self.project_id.cr_developer_currency_id.id,
                        "date": date.today(),
                        "partner_id": user.partner_id.id,
                        "invoice_line_ids": bill_lines,
                    }
                )

                for task in tasks:
                    dev = task.cr_developer_assignees_line.filtered(
                        lambda line: line.name == user and not line.cr_bill_id
                    )
                    dev.cr_bill_id = bill.id

            action = {
                "type": "ir.actions.act_window",
                "name": "Invoices",
                "res_model": "account.move",
                "view_mode": "tree,form",
                "domain": [("move_type", "=", "in_invoice")],
            }
            return action

        else:
            for task in self:
                for developer in task.cr_developer_assignees_line:
                    if not developer.cr_bill_id:
                        new_bill = self.env["account.move"].create(
                            {
                                "partner_id": developer.name.partner_id.id,
                                "ref": task.name,
                                "invoice_date": date.today(),
                                "date": date.today(),
                                "currency_id": developer.cr_currency_id.id,
                                "move_type": "in_invoice",
                                "invoice_line_ids": [
                                    (
                                        0,
                                        0,
                                        {
                                            "name": task.name,
                                            "quantity": 1,
                                            "analytic_distribution": {
                                                developer.cr_assignees_analytic_account_id.id: 100.0
                                            },
                                            "price_unit": developer.cr_developer_amount,
                                            "tax_ids": False,
                                        },
                                    )
                                ],
                            }
                        )

                        developer.cr_bill_id = new_bill.id

    def action_create_invoices(self, merge):
        """Create merge/separate invoices of customers of selected record from 'Action' in tree view of this model"""

        uom = self.env["uom.uom"].search([("name", "=", "Hours")], limit=1)
        odoo_product = self.env["product.product"].search(
            [("cr_odoo_service", "=", True)], limit=1
        )

        if merge:
            invoices = self.env["account.move"]
            project_wise_task = {}

            for task in self:
                if task.cr_approved_hours == 0:
                    raise ValidationError(
                        ("Cannot create an invoice of 'zero' Approved Hours")
                    )
                elif task.project_id not in project_wise_task:
                    project_wise_task[task.project_id] = []
                project_wise_task[task.project_id].append(task)

            for project, tasks in project_wise_task.items():
                invoice_lines = []
                task_count = 0
                for task in tasks:
                    if not task.cr_invoice_ids:
                        invoice_line_data = {
                            "product_id": odoo_product.id,
                            "name": task.name,
                            "product_uom_id": uom.id,
                            "analytic_distribution": {
                                task.project_id.analytic_account_id.id: 100.0
                            },
                            "quantity": task.cr_approved_hours,
                            "price_unit": task.cr_client_hourly_rate,
                            "tax_ids": False,
                        }
                        invoice_lines.append((0, 0, invoice_line_data))
                        task_count += 1

                if task_count != 0:
                    new_invoice = self.env["account.move"].create(
                        {
                            "move_type": "out_invoice",
                            "invoice_date": date.today(),
                            "date": date.today(),
                            "currency_id": self.project_id.cr_client_currency_id.id,
                            "partner_id": project.partner_id.id,
                            "payment_reference": project.name,
                            "invoice_line_ids": invoice_lines,
                        }
                    )

                    for task in tasks:
                        task.write({"cr_invoice_ids": [(4, new_invoice.id)]})

        else:
            odoo_product = self.env["product.product"].search(
                [("cr_odoo_service", "=", True)], limit=1
            )
            for task in self:
                if task.cr_approved_hours == 0:
                    raise ValidationError(
                        ("Cannot create an invoice of 'zero' Approved Hours")
                    )
            for task in self:
                if not task.cr_invoice_ids:
                    new_invoice = self.env["account.move"].create(
                        {
                            "partner_id": task.project_id.partner_id.id,
                            "payment_reference": task.name,
                            "invoice_date": date.today(),
                            "currency_id": task.project_id.cr_client_currency_id.id,
                            "move_type": "out_invoice",
                            "invoice_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": odoo_product.id,
                                        "name": task.name,
                                        "quantity": task.cr_approved_hours,
                                        "product_uom_id": uom.id,
                                        "analytic_distribution": {
                                            task.project_id.analytic_account_id.id: 100
                                        },
                                        "price_unit": task.cr_client_hourly_rate,
                                        "tax_ids": False,
                                    },
                                )
                            ],
                        }
                    )
                    task.write({"cr_invoice_ids": [(4, new_invoice.id)]})
        action = {
            "type": "ir.actions.act_window",
            "name": "Invoices",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "domain": [("move_type", "=", "out_invoice")],
        }
        return action

    def action_show_invoice(self):
        """Smart button action to show invoice/invoices of the respective task"""

        if self.cr_invoice_ids:
            action = {
                "type": "ir.actions.act_window",
                "name": "Invoice of Client",
                "res_model": "account.move",
                "context": {"create": False},
            }
            if len(self.cr_invoice_ids) == 1:
                action.update({"view_mode": "form", "res_id": self.cr_invoice_ids.id})
            else:
                action.update(
                    {
                        "view_type": "list",
                        "view_mode": "list,form",
                        "domain": [("id", "in", self.cr_invoice_ids.ids)],
                    }
                )
            return action

        else:
            raise ValidationError(("Create Invoice, First!!"))

    def action_show_all_bills(self):
        """Smart button action to show bill/bills of the respective task"""

        self.ensure_one()

        action = {
            "type": "ir.actions.act_window",
            "name": "Bills of Assignees",
            "res_model": "account.move",
            "context": {"create": False},
        }
        if (
            len(self.cr_developer_assignees_line) == 1
            and self.cr_developer_assignees_line.cr_bill_id
        ):
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.cr_developer_assignees_line.cr_bill_id.id,
                }
            )
        else:
            action.update(
                {
                    "view_type": "list",
                    "view_mode": "list,form",
                    "domain": [
                        ("id", "=", self.cr_developer_assignees_line.cr_bill_id.ids)
                    ],
                }
            )

        return action

    def merge_invoice_wizard_server_action(self):
        """Server action for popping-up wizard for merge invoice option"""
        return {
            "name": "Merge Invoice",
            "view_mode": "form",
            "res_model": "cr.merge.invoice",
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def merge_bill_wizard_server_action(self):
        """Server action for popping-up wizard for merge bill option"""

        return {
            "name": "Merge Bill",
            "view_mode": "form",
            "res_model": "cr.merge.bill",
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def create(self, vals):
        rec = super().create(vals)
        if vals[0].get("user_ids")[0][-1]:
            for user in (vals[0].get("user_ids"))[0][-1]:
                user_id = self.env["res.users"].browse(user)
                message = {
                    "title": f"New Task Created",
                    "message": f"You are assigned to \"{vals[0].get('name')}\"",
                    "task_id": rec.id
                }
                self.env["bus.bus"]._sendone(
                    user_id.partner_id, "cr_notification_task", message
                )
        else:
            pass
        return rec
