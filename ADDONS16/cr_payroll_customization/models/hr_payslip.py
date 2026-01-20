from odoo import api, fields, models
import calendar
from datetime import datetime, timedelta


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    total_working_days = fields.Float(
        string="Working Days", compute="compute_total_working_days"
    )

    @api.depends("contract_id")
    def compute_total_working_days(self):
        for rec in self:
            weekday = []
            for working_day in rec.contract_id.resource_calendar_id.attendance_ids:
                if working_day.dayofweek not in weekday:
                    weekday.append(int(working_day.dayofweek))
            current_date = rec.date_from.replace(day=1)
            last_day = calendar.monthrange(current_date.year, current_date.month)[1]
            end_date = current_date.replace(day=last_day)

            workdays_count = 0
            while current_date <= end_date:
                if (
                    current_date.weekday() in weekday
                ):
                    workdays_count += 1
                current_date += timedelta(days=1)
            rec.total_working_days = workdays_count

    @api.model
    def get_contract(self, employee, date_from, date_to):
        rec = super(HrPayslip, self).get_contract(employee, date_from, date_to)
        # a contract is valid if it ends between the given dates
        clause_1 = ["&", ("date_end", "<=", date_to), ("date_end", ">=", date_from)]
        # OR if it starts between the given dates
        clause_2 = ["&", ("date_start", "<=", date_to), ("date_start", ">=", date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = [
            "&",
            ("date_start", "<=", date_from),
            "|",
            ("date_end", "=", False),
            ("date_end", ">=", date_to),
        ]
        clause_final = (
            [
                ("employee_id", "=", employee.id),
                ("state", "in", ["open", "close"]),
                "|",
                "|",
            ]
            + clause_1
            + clause_2
            + clause_3
        )
        return self.env["hr.contract"].search(clause_final).ids
