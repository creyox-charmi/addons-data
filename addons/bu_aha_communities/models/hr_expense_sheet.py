# Copyright 2025 Efrat Rotenberg
# Part of module bu_aha_communities. inherit of hr.expense

from odoo import api, fields, models

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense'

    community_id = fields.Many2one(
        comodel_name='bu_community',
        compute='_compute_community_id',
        store=True,
    )

    event_id = fields.Many2one(
        comodel_name='calendar.event',
        compute='_compute_event_id',
        store=True,
    )

    related_to = fields.Selection(
        selection=[
            ("community", "Community (General)"),
            ("event", "Community (Event)"),
        ],
        compute='_compute_related_to',
        store=True,
    )

    @api.depends('expense_line_ids.community_id')
    def _compute_community_id(self):
        for sheet in self:
            communities = sheet.expense_line_ids.mapped('community_id')
            sheet.community_id = communities[0] if communities else False

    @api.depends('expense_line_ids.event_id')
    def _compute_event_id(self):
        for sheet in self:
            events = sheet.expense_line_ids.mapped('event_id')
            sheet.event_id = events[0] if events else False

    @api.depends('expense_line_ids.related_to')
    def _compute_related_to(self):
        for sheet in self:
            related = sheet.expense_line_ids.mapped('related_to')
            sheet.related_to = related[0] if related else False
