# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    supervisor_id = fields.Many2one("res.users", string="Supervisor Name")
    total_expected_duration = fields.Float(
        "Total Expected Duration",
        compute="_compute_total_expected_duration",
        store=True,
    )
    total_real_duration = fields.Float(
        "Total Real Duration", compute="_compute_total_real_duration", store=True
    )
    fluctuation_reason = fields.Text("Fluctuation Reason")

    @api.depends("workorder_ids.duration_expected", "workorder_ids.grace_time")
    def _compute_total_expected_duration(self):
        """
        Computes the total expected duration by summing up the expected
        durations and grace times of all associated work orders.
        """
        duration_expected = 0
        grace_time = 0

        # Loop through each work order to calculate total expected duration.
        for record in self.workorder_ids:
            duration_expected += record.duration_expected
            grace_time += record.grace_time

        # Set the total expected duration field.
        self.total_expected_duration = duration_expected + grace_time

    @api.depends("workorder_ids.duration")
    def _compute_total_real_duration(self):
        """
        Computes the total real duration by summing up the actual durations
        of all associated work orders.
        """
        duration = 0

        # Loop through each work order to calculate total real duration.
        for record in self.workorder_ids:
            duration += record.duration

            # Set the total real duration field.
        self.total_real_duration = duration

    def button_mark_done(self):
        """
        Overrides the button to mark the production as done. Validates
        that if there is a significant difference between expected and
        actual durations, a fluctuation reason is provided.
        """
        res = super(MrpProduction, self).button_mark_done()

        for record in self:
            if record.total_expected_duration:
                if record.total_real_duration:
                    difference = abs(
                        record.total_expected_duration - record.total_real_duration
                    )

                    # Check if the difference exceeds the threshold of 15.
                    if difference >= 15:
                        # If there is no fluctuation reason provided, raise an error.
                        if not record.fluctuation_reason:
                            raise UserError("Fluctuation Reason is required.")

        return res
