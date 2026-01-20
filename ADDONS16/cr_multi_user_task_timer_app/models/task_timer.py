# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, api, fields
from odoo import http
from odoo.http import request


class TaskTimer(models.Model):
    _name = "task.timer"
    _description = "records the timer of the task of a particular user"

    task_id = fields.Many2one("project.task", string="Task", required=True)
    user_id = fields.Many2one(
        "res.users", string="User", required=True, default=lambda self: self.env.user
    )
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="Pause Time")
    duration = fields.Float(string="Duration (Hours)", store=True, default=0)
    state = fields.Selection(
        [("running", "Running"), ("paused", "Paused"), ("stopped", "Stopped")],
        string="Status",
    )
    is_pause_of_stop = fields.Boolean(default=False)


class TaskTimerController(http.Controller):
    @http.route('/task/timer/status', type='json', auth='user')
    def get_task_timer_status(self, task_id):
        """
        Custom endpoint to fetch timer status for a specific task and user.
        """
        user_id = request.env.user.id
        task_timer = request.env['task.timer'].search([
            ('task_id', '=', task_id),
            ('user_id', '=', user_id),
        ], limit=1)
        
        if task_timer:
            return {
                'state': task_timer.state,
                'duration': task_timer.duration,
                'start_time': task_timer.start_time,
                'is_pause_of_stop': task_timer.is_pause_of_stop,
            }
        return 0


