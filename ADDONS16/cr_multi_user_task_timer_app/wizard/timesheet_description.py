# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields
from datetime import date
from odoo.exceptions import ValidationError


class TimesheetDescriptionWizard(models.TransientModel):
    _name = "timesheet.description.wizard"
    _description = "Wizard for Timesheet Description"

    name = fields.Char(string="Description")
    task_id = fields.Many2one("project.task")

    def action_create_timesheet(self):
        """
        Creates a timesheet entry in the 'account.analytic.line' model for the current
        employee based on the time spent on the task as recorded by the task timer.
        The task timer's state is set to 'stopped' and its duration reset to zero.

        This method is executed when the user clicks the "Save" button in the wizard.
        """
        # Get the timesheet model
        if not self.name:
            raise ValidationError(f"The Description field is mandatory ")

        timesheet_model = self.env["account.analytic.line"]

        # Get the current employee linked to the current user
        current_employee = self.env["hr.employee"].search(
            [("user_id", "=", self.env.user.id)], limit=1
        )

        # Get the task timer for the current user and task
        task_timer = self.env["task.timer"].search(
            [("user_id", "=", self.env.user.id), ("task_id", "=", self.task_id.id)]
        )

        # Create the timesheet entry
        timesheet_model.sudo().create(
            {
                "name": self.name,
                "employee_id": current_employee.id,
                "date": date.today(),
                "task_id": self.task_id.id,
                "project_id": self.task_id.project_id.id,
                "unit_amount": task_timer.duration,
            }
        )

        task_timer.write(
            {"state": "stopped", "duration": 0.0, "is_pause_of_stop": False}
        )

        return {"type": "ir.actions.act_window_close"}

    def action_cancel_time(self):
        """
        The method resumes or pauses based on the user's previous choice.
        """
        task_timer = self.env["task.timer"].search(
            [("user_id", "=", self.env.user.id), ("task_id", "=", self.task_id.id)]
        )
        start_time = fields.Datetime.now()
        if task_timer.state == "running":
            task_timer.write(
                {"start_time": start_time, "is_pause_of_stop": False, "end_time": False}
            )
        elif task_timer.state == "paused":
            task_timer.write(
                {"start_time": False, "is_pause_of_stop": False, "end_time": False}
            )

        return {"type": "ir.actions.act_window_close"}
