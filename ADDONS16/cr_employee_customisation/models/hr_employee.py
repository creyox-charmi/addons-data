from odoo import fields, models, api
from datetime import date


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Fields for employee's special days celebration
    next_birthday = fields.Integer(
        string="Next Birthday", compute="_compute_next_birthday"
    )
    next_anniversary = fields.Integer(
        string="Next Anniversary", compute="_compute_next_anniversary"
    )
    birthday_msg = fields.Char(string="Birthday Message")
    anniversary_msg = fields.Char(string="Anniversary Message")

    # Fields for paid leaves of employee
    taken_paid_leaves = fields.Float(
        string="Taken Paid Leaves", compute="_compute_taken_paid_leaves"
    )
    remaining_paid_leaves = fields.Float(
        string="Remaining Paid Leaves", compute="_compute_remaining_paid_leaves"
    )

    # Extend contract
    contract_lines = fields.One2many("hr.contract", "employee_id", string="Contracts")

    @api.depends("birthday")
    def _compute_next_birthday(self):
        for record in self:
            today = date.today()
            if record.birthday:
                this_year_birthday = record.birthday.replace(year=today.year)
                if this_year_birthday < today:
                    next_birthday_date = record.birthday.replace(year=today.year + 1)
                else:
                    next_birthday_date = this_year_birthday
                record.next_birthday = (next_birthday_date - today).days
            else:
                record.next_birthday = 0

    @api.depends("contract_lines.date_start")
    def _compute_next_anniversary(self):
        for record in self:
            today = date.today()
            contracts = record.contract_lines.sorted(key=lambda c: c.date_start)
            join_date = contracts[0].date_start if contracts else False

            if join_date:
                next_anniversary_date = join_date.replace(year=today.year)
                if next_anniversary_date < today:
                    next_anniversary_date = join_date.replace(year=today.year + 1)
                record.next_anniversary = (next_anniversary_date - today).days
            else:
                record.next_anniversary = 0

    @api.depends()
    def _compute_taken_paid_leaves(self):
        for record in self:
            paid_leaves = self.env["hr.leave"].search(
                [
                    ("employee_id", "=", record.id),
                    ("holiday_status_id.leave_type", "=", "paid"),
                    ("state", "=", "validate"),
                ]
            )
            record.taken_paid_leaves = sum(leave.number_of_days for leave in paid_leaves)

    @api.depends()
    def _compute_remaining_paid_leaves(self):
        for record in self:
            paid_leave_allocation = self.env["hr.leave.allocation"].search(
                [
                    ("employee_id", "=", record.id),
                    ("state", "=", "validate"),
                    ("holiday_status_id.leave_type", "=", "paid"),
                ],
                limit=1,
            )
            total_days = paid_leave_allocation.number_of_days_display if paid_leave_allocation else 0
            record.remaining_paid_leaves = total_days - record.taken_paid_leaves


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    birthday_msg = fields.Char(string="Birthday Message")
    anniversary_msg = fields.Char(string="Anniversary Message")
