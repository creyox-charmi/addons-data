# Copyright 2022 Yves Goldberg (Ygol InternetWork)
# Part of module bu_aha_communities. See LICENSE file for
# full copyright and licensing details.

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # community_id = fields.Many2one("bu_aha_communities.bu_community")
    community_id = fields.Many2one("bu_community", readonly=True)
    reported_id = fields.Many2one('calendar.report',copy=False)
    # has_community = fields.Boolean(default=False)

    expected1 = fields.Integer()
    expected2 = fields.Integer()
    expected3 = fields.Integer()
    expected4 = fields.Integer()
    attended1 = fields.Integer()
    attended2 = fields.Integer()
    attended3 = fields.Integer()
    attended4 = fields.Integer()
    total_expected = fields.Integer(compute="_compute_total_expected",
                                    readonly=True)
    total_attended = fields.Integer(compute="_compute_total_attended",
                                    readonly=True)
    attending_member = fields.Many2one(
        comodel_name="res.partner", domain=[("community_id", "!=", False)]
    )  # [("community_id", "!=", False)])  # domain: community_id = (this)community_id?
    # contact_mobile = fields.Char(compute="_compute_contact_mobile", readonly=True)
    contact_mobile = fields.Char(related="attending_member.phone")
    lecturer = fields.Many2one(comodel_name="res.partner")
    degree = fields.Selection(related="lecturer.degree")
    degree_theme = fields.Selection(related="lecturer.degree_theme")
    expense_ids = fields.Many2many("hr.expense")
    total_expenses = fields.Integer(compute="_compute_total_expenses",
                                    readonly=True,store=True)
    expected_expenses = fields.Integer()
    following_community_ids = fields.Many2many("bu_community", 'cm_events',
                                               "col1", "col2", store=True,
                                               compute="get_following_community")
    following_community_event_ids = fields.Many2many("calendar.event",
                                                     "events_of_cms", "cm1",
                                                     "cm2",
                                                     store=True,
                                                     compute="get_following_community")
    show_to_user = fields.Boolean(compute="get_user_visibility", store=True)

    @api.depends('following_community_event_ids', 'following_community_ids')
    def get_user_visibility(self):
        user = self.env.user
        for rec in self:
            if user and rec.id in rec.following_community_event_ids.ids:
                rec.show_to_user = True
            else:
                rec.show_to_user = False

    @api.depends("community_id")
    def get_following_community(self):
        for rec in self:
            community_ids = self.env['bu_community'].search(
                ['|', ('message_is_follower', '=', True),
                 ('responsible_id', '=', self.env.user.id)])
            if community_ids:
                rec.following_community_ids = [(6, 0, community_ids.ids)]
                events = []
                for i in community_ids:
                    for j in i.event_ids:
                        events.append(j.id)
                rec.following_community_event_ids = [(6, 0, events)]
            else:
                rec.following_community_ids = [(6, 0, [])]
                rec.following_community_event_ids = [(6, 0, [])]

    @api.depends("expense_ids")
    def _compute_total_expenses(self):
        for record in self:
            sum = 0
            for expense in record.expense_ids:
                sum += expense.total_amount
            record.total_expenses = sum

    # attending_member_domain = fields.Char(
    #     compute="_compute_attending_member_domain",
    #     readonly=True,
    #     store=False
    # )

    # @api.depends('community_id')
    # def _compute_attending_member_domain(self):
    #     for r in self:
    #         if r.community_id:
    #             r.attending_member_domain =
    #              json.dumps([('community_id','=',r.community_id.id)])
    #         else:
    #             r.attending_member_domain = "[('community_id', '!=', False)]"

    # def _calculate_attending_domain(self):
    #     for r in self:
    #         if r.community_id:
    #             return    [("community_id", "=", r.community_id)]
    #         else:
    #             return [("False", "=", "True")]

    # @api.onchange("community_id")
    # def _onchange_attending_member(self):
    #     for r in self:
    #         return {'domain': {'attending_member': [('community_id','=',r.community_id.id)]}}

    @api.depends("attending_member")
    def _compute_contact_mobile(self):
        for r in self:
            if r.attending_member and r.attending_member.phone:
                r.contact_mobile = r.attending_member.phone
            else:
                r.contact_mobile = ""

    @api.depends("expected1", "expected2", "expected3", "expected4")
    def _compute_total_expected(self):
        for r in self:
            r.total_expected = r.expected1 + r.expected2 + r.expected3 + r.expected4

    @api.depends("attended1", "attended2", "attended3", "attended4")
    def _compute_total_attended(self):
        for r in self:
            r.total_attended = r.attended1 + r.attended2 + r.attended3 + r.attended4

    def get_menu_action(self):
        user = self.env.user
        manager = user.has_group(
            "bu_aha_communities.bu_community_group_manager")
        domain = []
        if manager:
            domain.append(('community_id', '!=', False))
        else:
            domain.append(('show_to_user', '=', True))

        community_ids = self.env['bu_community'].search(
            ['|', ('message_is_follower', '=', True),
             ('responsible_id', '=', self.env.user.id)]).mapped("event_ids")

        if user.has_group('bu_aha_communities.bu_community_group_user'):
            domain = [('id', 'in', community_ids.ids)]
        if user.has_group('base.group_system') or manager:
            domain = []

        # for rec in community_ids:
        #     rec.community_id = rec.community_id.id
        return {
            'name': "Community Events",
            'view_mode': 'list,form',
            'view_type': "form",
            'res_model': 'calendar.event',
            'target': 'self',
            'view_ids': [(False, 'list'),
                         (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': domain
        }

    # @api.model
    # def create(self, vals):
    #     res = super(CalendarEvent, self).create(vals)
    #     community_id = vals.get("community_id")
    #     all_communities = self.env["bu_community"].search([])
    #     for community in all_communities:
    #         if community.id == community_id:
    #             id_list = []
    #             for partner in community.event_ids:
    #                 id_list.append(partner.id)
    #             id_list.append(res.id)
    #             community.write({"event_ids": [[6, 0, id_list]]})
    #     all_communities = self.env["bu_community"].search([])
    #     return res

    # def write(self, vals):
    #     former = self.community_id
    #     res = super(CalendarEvent, self).write(vals)
    #     community_id = vals.get("community_id")
    #     if former:
    #         id_list = []
    #         for partner in former.event_ids:
    #             if partner.id != self.id:
    #                 id_list.append(partner.id)
    #         former.write({"event_ids": [[6, 0, id_list]]})
    #     if not community_id:
    #         return res
    #     all = self.env["bu_community"].search([])
    #     for community in all:
    #         if community.id == community_id:
    #             id_list = [self.id]
    #             for partner in community.event_ids:
    #                 id_list.append(partner.id)
    #             community.write({"event_ids": [[6, 0, id_list]]})
    #     return res
