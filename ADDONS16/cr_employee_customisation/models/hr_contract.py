from odoo import models, fields
from datetime import date, timedelta
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    _inherit = "hr.contract"

    leaves_of_contract = fields.Float(
        string="Leaves of Current Contract (in days)",
        compute="_compute_leaves_of_contract",
        default=0,
    )

    is_extended = fields.Boolean(default=False)

    def _compute_leaves_of_contract(self):
        """Calculates the number of leaves of the contract in days"""
        for record in self:
            total_leaves = 0.0
            leaves = self.env["hr.leave"].search(
                [
                    ("employee_id", "=", record.employee_id.id),
                    ("date_from", ">=", record.date_start),
                    ("date_from", "<=", record.date_end),
                ]
            )

            for leave in leaves:
                total_leaves += leave.number_of_days

            record.leaves_of_contract = total_leaves

    def action_log_to_chatter(self, extended_days):
        """Logs a message in the chatter about contract extension"""
        for contract in self:
            contract.message_post(
                body=f"The contract has been extended by {extended_days} days.",
                subject="Contract Extension",
                message_type="notification",
                subtype_xmlid="mail.mt_note",
            )

    def action_extend_contract(self):
        """Extends the contract and creates a new one"""
        for record in self:
            record.is_extended = True

            # Calculate new contract details
            extended_days = round(record.leaves_of_contract)
            new_date_start = record.date_end + timedelta(days=1)
            new_date_end = record.date_end + timedelta(days=extended_days)

            # Create the new contract
            new_contract = self.env["hr.contract"].create(
                {
                    "employee_id": record.employee_id.id,
                    "date_start": new_date_start,
                    "date_end": new_date_end,
                    "name": f"{record.employee_id.name}'s extended contract",
                    "wage": record.wage,
                    "structure_type_id": record.structure_type_id.id,
                    "hr_responsible_id": record.hr_responsible_id.id,
                    "resource_calendar_id": record.resource_calendar_id.id,
                    "struct_id": record.struct_id.id,
                    "state": "draft",
                }
            )

            if new_contract:
                new_contract.action_log_to_chatter(extended_days)
            else:
                raise ValidationError("Failed to create a new extended contract.")

            # Open the new contract form view
            return {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "views": [(False, "form")],
                "res_model": "hr.contract",
                "res_id": new_contract.id,
                "target": "current",
            }
