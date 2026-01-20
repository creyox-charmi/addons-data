# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProjectTaskTimer(models.Model):
    _inherit = "project.task"

    task_timer_ids = fields.One2many("task.timer", "task_id")
    time_count = fields.Float(
        "Time", compute="_compute_duration", store=True, default=0
    )

    display_start = fields.Boolean(default=True, compute="compute_display_start")
    display_stop = fields.Boolean(default=False, compute="compute_display_stop")
    display_pause = fields.Boolean(default=False, compute="compute_display_pause")
    display_resume = fields.Boolean(default=False, compute="compute_display_resume")
    active_user_working_status = fields.Char(
        compute="compute_active_user_working_status"
    )
    user_id = fields.Many2one("res.users", compute="compute_user_id")
    is_current_user_assigned = fields.Boolean(
        compute="_compute_is_current_user_assigned",
        store=False
    )

    @api.depends('user_ids')
    def _compute_is_current_user_assigned(self):
        current_user = self.env.user
        for record in self:
            record.is_current_user_assigned = current_user in record.user_ids

    @api.depends("user_ids")
    def compute_user_id(self):
        """
        Compute the current user ID if the user is assigned to the task.
        """
        for record in self:
            record.user_id = False
            if self.env.user in record.user_ids:
                record.user_id = self.env.user.id

    @api.depends("task_timer_ids.state")
    def compute_active_user_working_status(self):
        """
        Compute the working status (running, paused, stopped) for the current user based on
        the latest task timer entry for the task.
        """
        for record in self:
            res = record.task_timer_ids.search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("task_id", "=", record.id),
                ],
                limit=1,
                order="id desc",
            )
            if res:
                record.active_user_working_status = res.state
            else:
                record.active_user_working_status = "stopped"

    @api.depends("task_timer_ids.state")
    def compute_display_start(self):
        """
        Compute the visibility of the start button. The start button will be hidden
        if the task is already running or paused.
        """
        for record in self:
            res = record.task_timer_ids.search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("task_id", "=", record.id),
                ],
                limit=1,
                order="id desc",
            )
            if res and res.state in ["running", "paused"]:
                record.display_start = False
            else:
                record.display_start = True

    @api.depends("task_timer_ids.state")
    def compute_display_stop(self):
        """
        Compute the visibility of the stop button. The stop button will be hidden
        if the task timer is already stopped.
        """
        for record in self:
            res = record.task_timer_ids.search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("task_id", "=", record.id),
                ],
                limit=1,
                order="id desc",
            )
            record.display_stop = res and res.state != "stopped"

    @api.depends("task_timer_ids.state")
    def compute_display_pause(self):
        """
        Compute the visibility of the pause button. The pause button will be shown
        only if the task is currently running.
        """
        for record in self:
            res = record.task_timer_ids.search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("task_id", "=", record.id),
                ],
                limit=1,
                order="id desc",
            )
            record.display_pause = res and res.state == "running"

    @api.depends("task_timer_ids.state")
    def compute_display_resume(self):
        """
        Compute the visibility of the resume button. The resume button will be shown
        only if the task is currently paused.
        """
        for record in self:
            res = record.task_timer_ids.search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("task_id", "=", record.id),
                ],
                limit=1,
                order="id desc",
            )
            record.display_resume = res and res.state == "paused"

    @api.depends("task_timer_ids")
    def _compute_duration(self):
        """
        Compute the total time spent on the task by the current user. If the task
        is running, the duration will include the current session's active time.
        """
        for record in self:
            res = record.task_timer_ids.search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("task_id", "=", record.id),
                ],
                limit=1,
                order="id desc",
            )
            if res:
                total_duration = res.duration
                if res.state == "running" and res.start_time:
                    current_duration = round(
                        (fields.Datetime.now() - res.start_time).total_seconds()
                        / 3600.0,
                        6,
                    )
                    record.time_count = total_duration + current_duration
                else:
                    record.time_count = total_duration

    def start_task(self):
        """
        Start a new timer for the task. Ensure that no other task is running for the current
        user. If a timer already exists for the task and it is stopped, restart the timer.
        """
        # Ensure only one running timer per user
        user_tasks = self.env["project.task"].search(
            [
                ("user_ids", "=", self.env.user.id),
                ("id", "!=", self.id),
            ]
        )
        for task in user_tasks:
            if task.active_user_working_status == "running":
                raise ValidationError(f"Task: '{task.name}' is still running")

        res = self.task_timer_ids.search(
            [
                ("user_id", "=", self.env.user.id),
                ("task_id", "=", self.id),
            ],
            limit=1,
            order="id desc",
        )

        if not res:
            self.env["task.timer"].create(
                {
                    "task_id": self.id,
                    "user_id": self.env.user.id,
                    "start_time": fields.Datetime.now(),
                    "state": "running",
                    "duration": 0,
                }
            )
        elif res.state == "stopped":
            res.write(
                {
                    "start_time": fields.Datetime.now(),
                    "end_time": False,
                    "state": "running",
                    "duration": 0,
                }
            )
        else:
            raise ValidationError(f"Your task '{self.name}' has not stopped yet")

    def pause_timer(self):
        """
        Pause the currently running timer for the task and update the duration.
        """
        res = self.task_timer_ids.search(
            [
                ("user_id", "=", self.env.user.id),
                ("task_id", "=", self.id),
            ],
            limit=1,
            order="id desc",
        )

        if res and res.state == "running":
            end_time = fields.Datetime.now()
            duration = round((end_time - res.start_time).total_seconds() / 3600.0, 6)
            res.write(
                {
                    "end_time": end_time,
                    "state": "paused",
                    "duration": res.duration + duration,
                }
            )

    def stop_timer(self):
        """
        Stop the currently running or paused timer and record the final duration.
        Opens a wizard to enter a timesheet description.
        """
        res = self.task_timer_ids.search(
            [
                ("user_id", "=", self.env.user.id),
                ("task_id", "=", self.id),
            ],
            limit=1,
            order="id desc",
        )

        if res and res.state != "stopped":
            duration = 0
            if res.start_time and res.end_time:
                res.write(
                    {
                        "is_pause_of_stop": True,
                    }
                )
            elif res.start_time:
                end_time = fields.Datetime.now()
                duration = round(
                    (end_time - res.start_time).total_seconds() / 3600.0, 6
                )
                res.write(
                    {
                        "end_time": end_time,
                        "is_pause_of_stop": True,
                        "duration": res.duration + duration,
                    }
                )

        # Open timesheet description wizard
        return {
            "name": "Timesheet Work Description",
            "type": "ir.actions.act_window",
            "res_model": "timesheet.description.wizard",
            "view_mode": "form",
            "view_id": self.env.ref(
                "cr_multi_user_task_timer_app.view_timesheet_description_wizard"
            ).id,
            "target": "new",
            "context": {
                "default_task_id": self.id,
            },
        }

    def unpause_timer(self):
        """
        Resume a paused timer for the task. Ensures no other task is currently running
        for the current user before resuming.
        """
        # Ensure no other task is running before resuming
        user_tasks = self.env["project.task"].search(
            [
                ("user_ids", "=", self.env.user.id),
                ("id", "!=", self.id),
            ]
        )
        for task in user_tasks:
            if task.active_user_working_status == "running":
                raise ValidationError(f"Task: '{task.name}' is still running")

        res = self.task_timer_ids.search(
            [
                ("user_id", "=", self.env.user.id),
                ("task_id", "=", self.id),
            ],
            limit=1,
            order="id desc",
        )

        if res:
            res.write(
                {
                    "start_time": fields.Datetime.now(),
                    "end_time": False,
                    "state": "running",
                }
            )

