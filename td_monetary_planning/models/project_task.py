# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import models, fields,api
import logging
from odoo import models
from datetime import time as dt_time
_logger = logging.getLogger(__name__)

class ProjectTaskCl(models.Model):
    _inherit = 'project.task'

    amount_cost = fields.Float(
        string='Cost'
    )
    amount_target = fields.Float(
        string='Target'
    )
    price_subtotal = fields.Float(
        string='Sale'
    )

    subtask_percentage = fields.Float(
        string="Subtask % of Parent",
        compute="_compute_subtask_percentage",
    )

    @api.depends("ks_start_datetime", "ks_end_datetime", "parent_id.ks_start_datetime",
                 "parent_id.ks_end_datetime", "child_ids.ks_start_datetime",
                 "child_ids.ks_end_datetime")
    def _compute_subtask_percentage(self):
        """
        Compute method for subtask_percentage
        Uses ks_compute_percentage() for each record.
        """
        for task in self:
            try:
                percentage = task.ks_compute_percentage()
                task.subtask_percentage = percentage
            except Exception as e:
                _logger.error(f"Error computing percentage for task {task.id}: {e}")
                task.subtask_percentage = 0.0

    def _get_root_parent(self):
        """Get the topmost parent task (root of hierarchy)"""
        self.ensure_one()
        current = self
        while current.parent_id:
            current = current.parent_id
        return current

    def _get_all_descendants(self):
        """Get all descendant tasks recursively"""
        self.ensure_one()
        descendants = self.env['project.task']

        def collect_children(task):
            nonlocal descendants
            for child in task.child_ids:
                descendants |= child
                collect_children(child)

        collect_children(self)
        return descendants

    def ks_compute_percentage(self):
        """Return percentage based on root parent duration"""
        self.ensure_one()
        start_date = self.ks_start_datetime
        end_date = self.ks_end_datetime

        # If task has no dates, return 0
        if not start_date or not end_date:
            return 0.0

        # Get the root parent (topmost task)
        root_parent = self._get_root_parent()

        # If this task IS the root parent (has no parent)
        if root_parent == self:
            # Sum percentages of all descendants
            all_descendants = self._get_all_descendants()
            total = 0.0

            for descendant in all_descendants:
                if descendant.ks_start_datetime and descendant.ks_end_datetime:
                    task_duration = (descendant.ks_end_datetime - descendant.ks_start_datetime).days
                    if root_parent.ks_start_datetime and root_parent.ks_end_datetime:
                        root_duration = (root_parent.ks_end_datetime - root_parent.ks_start_datetime).days or 1
                        descendant_percentage = (task_duration / root_duration) * 100
                        total += descendant_percentage

            return round(total, 2)

        # If this task has a parent, calculate based on root parent
        else:
            if root_parent.ks_start_datetime and root_parent.ks_end_datetime:
                root_duration = (root_parent.ks_end_datetime - root_parent.ks_start_datetime).days or 1
                task_duration = (end_date - start_date).days
                percentage = round((task_duration / root_duration) * 100, 2)
                return percentage
            return 0.0

