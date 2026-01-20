from odoo import fields, models


class HrLeave(models.Model):
    _inherit = "hr.leave.type"

    leave_type = fields.Selection(
        string="Leave Type",
        selection=[
            ("paid", "Paid Leave"),
            ("unpaid", "Unpaid Leave"),
            ("sick", "Sick Leave"),
        ],
    )
