# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HelpdeskStage(models.Model):
    _name = "helpdesk.stage"
    _description = "Helpdesk Stage"
    _order = "sequence"

    name = fields.Char(string="Stage Name", required=True)
    sequence = fields.Integer("Sequence", default=1)

    def unlink(self):
        for stage in self:
            # Check if there are any helpdesk tickets associated with this stage
            ticket_count = self.env["helpdesk.ticket"].search_count(
                [("stage_id", "=", stage.id)]
            )
            if ticket_count > 0:
                raise ValidationError(
                    "You cannot delete this stage because there are helpdesk tickets associated with it."
                )
        return super(HelpdeskStage, self).unlink()
