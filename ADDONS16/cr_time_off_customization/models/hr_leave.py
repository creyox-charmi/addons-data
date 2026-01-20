from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime


class HrLeave(models.Model):
    _inherit = "hr.leave"

    name = fields.Char(string = 'Description', required = True)
    number_of_hours_display = fields.Float(
        "Duration in hours",
        compute="_compute_number_of_hours_display",
        readonly=True,
        store=True,
        help="Number of hours of the time off request according to your working schedule. Used for interface.",
    )

    @api.constrains("number_of_hours_display")
    def _check_number_of_hours_display(self):
        """this function doesn't allow to keep paid leaves per month and also adds pending paid leave hrs to next month"""
        for record in self:

            # Calculate the first and last day of the created leave month
            if record.holiday_status_id.leave_type == 'paid':
                day_of_leave = record.date_from
                contracts = self.env["hr.contract"].search(
                    [
                        ("employee_id", "=", record.employee_id.id),
                        ("state", "in", ["open", "close"]),
                    ]
                )
                min_date = min([contract.date_start for contract in contracts])
                if min_date.year == datetime.now().year:
                    first_day = min_date
                else:
                    first_day = day_of_leave.replace(day=1, month=1)
                next_month = day_of_leave.replace(
                    month=(day_of_leave.month % 12) + 1, day=1
                )
                last_day = next_month - timedelta(days=1)

                # Search for paid leaves within the same month for the same employee
                paid_leave_type = self.env["hr.leave.type"].search(
                    [("leave_type", "=", "paid")], limit=1
                )

                leaves = self.env["hr.leave"].search(
                    [
                        ("employee_id", "=", record.employee_id.id),
                        ("holiday_status_id", "=", paid_leave_type.id),
                        ("date_from", ">=", first_day),
                        ("date_from", "<=", last_day),
                    ]
                )

                # Calculate total hours including the current record
                count_hours = 0
                for leave in leaves:
                    count_hours += leave.number_of_hours_display

                # Check if the hours exceed the monthly limit
                holiday_allocation = self.env["hr.leave.allocation"].search(
                    [
                        ("employee_id", "=", record.employee_id.id),
                        ("holiday_status_id", "=", paid_leave_type.id),
                    ]
                )
                count_months = last_day.month - first_day.month + 1
                if count_hours > (
                    (holiday_allocation.number_of_hours_display / 12) * count_months
                ):
                    raise ValidationError(
                        "Your limitation for paid leave is over for this month"
                    )

    def format_date(self, date_string):
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")

        day = date_obj.day
        month = date_obj.strftime("%b")  # Short month name (Oct, Nov, etc.)
        year = date_obj.year

        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

        # Return the formatted date string
        return f"{day}{suffix} {month}, {year}"

    def create(self, vals):
        """when leave gets created by employee the admins gets notification regarding the same"""
        holiday = super().create(vals)
        group_system = self.env.ref("base.group_system")

        users_with_admin_settings = self.env["res.users"].search(
            [("groups_id", "in", group_system.id)]
        )

        for user in users_with_admin_settings:
            if holiday.request_date_from != holiday.request_date_to:
                message = {
                    "title": f"{holiday.employee_id.name} created leave",
                    "type": "warning",
                    "message": f"from {self.format_date(str(holiday.request_date_from))} to {self.format_date(str(holiday.request_date_to))}",
                    "sticky": True,
                }
            else:
                message = {
                    "title": f"{holiday.employee_id.name} created leave",
                    "type": "warning",
                    "message": f"on {self.format_date(str(holiday.request_date_from))}",
                    "sticky": True,
                }
            self.env["bus.bus"]._sendone(
                user.partner_id, "simple_notification", message
            )
        return holiday

    def write(self, vals):
        """when leave gets approved the notification will be sent to the respective employee"""
        holiday = super(HrLeave, self).write(vals)
        if holiday:
            for record in self:
                if 'state' in vals and vals.get("state") == 'validate':
                    message = {
                        "title": f"Leave approved",
                        "type": "success",
                        "message": f"Great news! Your leave has been approved",
                        "sticky": True,
                    }
                    self.env["bus.bus"]._sendone(
                        record.employee_id.user_id.partner_id,
                        "simple_notification",
                        message,
                    )
                elif 'state' in vals and vals.get("state") == 'refuse':
                    message = {
                        "title": f"Leave Denied",
                        "type": "danger",
                        "message": f"Your leave has been denied.",
                        "sticky": True,
                    }
                    self.env["bus.bus"]._sendone(
                        record.employee_id.user_id.partner_id,
                        "simple_notification",
                        message,
                    )
                else:
                    pass

        return holiday
    
    
    def leave_refusal(self):
        for leave in self:
            leave.write({
                'state' : 'refuse',
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leaves',
            'res_model': 'hr.leave',
            'view_mode': 'tree,form',
            'target': 'current',
        }
        