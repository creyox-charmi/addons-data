# Copyright 2022 Yves Goldberg (Ygol InternetWork)
# Part of module bu_aha_communities. See LICENSE file for
# full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class BuCommunity(models.Model):
    _name = "bu_community"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Bu Community"

    class Constraint(models.Constraint):
        _check_name_unique = ("unique (name)", "The name must be unique.")

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    member_ids = fields.Many2many(
        string="Members",
        comodel_name="res.partner",
        # inverse_name="community_id",
        domain=[("is_company", "=", False)],
    )

    employee_ids = fields.Many2many(
        string="Workers",
        comodel_name="hr.employee",
    )

    @api.model
    def create(self, vals_list):
        # Create records first
        records = super(BuCommunity, self).create(vals_list)

        # Handle both single dict and list of dicts
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
            single_record = True
        else:
            single_record = False

        # Pair each vals dict with its created record
        for vals, res in zip(vals_list, records):

            employee_ids = vals.get("employee_ids")
            member_ids = vals.get("member_ids")
            expense_ids = vals.get("expense_ids")
            event_ids = vals.get("event_ids")

            # Handle employee_ids
            if employee_ids and isinstance(employee_ids, list) and len(employee_ids) > 0:
                if isinstance(employee_ids[0], (list, tuple)) and len(employee_ids[0]) >= 3:
                    actual_employee_ids = employee_ids[0][2]
                    if actual_employee_ids:
                        existing_employees = self.env["hr.employee"].browse(actual_employee_ids).filtered(
                            lambda e: e.community_id and e.community_id != res
                        )
                        if existing_employees:
                            raise UserError(
                                _("The employee %s already belongs to an existing community.")
                                % existing_employees[0].name
                            )
                        self.env["hr.employee"].browse(actual_employee_ids).write(
                            {"community_id": res.id}
                        )

            # Handle member_ids
            if member_ids and isinstance(member_ids, list) and len(member_ids) > 0:
                if isinstance(member_ids[0], (list, tuple)) and len(member_ids[0]) >= 3:
                    actual_member_ids = member_ids[0][2]
                    if actual_member_ids:
                        existing_members = self.env["res.partner"].browse(actual_member_ids).filtered(
                            lambda m: m.community_id and m.community_id != res
                        )
                        if existing_members:
                            raise UserError(
                                _("The member %s already belongs to an existing community.")
                                % existing_members[0].name
                            )
                        self.env["res.partner"].browse(actual_member_ids).write(
                            {"community_id": res.id}
                        )

            # Handle event_ids with safety checks
            if event_ids and isinstance(event_ids, list) and len(event_ids) > 0:
                if isinstance(event_ids[0], (list, tuple)) and len(event_ids[0]) >= 3:
                    actual_event_ids = event_ids[0][2]
                    if actual_event_ids:
                        events_to_link = self.env["calendar.event"].browse(actual_event_ids)

                        existing_events = events_to_link.filtered(
                            lambda e: e.community_id and e.community_id != res
                        )
                        if existing_events:
                            raise UserError(
                                _("The event %s is attributed to an existing community.")
                                % existing_events[0].name
                            )

                        for event in events_to_link:
                            event.community_id = res.id
                            if event.recurrency and event.recurrence_id:
                                recurring_events = event.recurrence_id.calendar_event_ids
                                recurring_events.write({"community_id": res.id})
                                new_event_ids = list(
                                    set(actual_event_ids + recurring_events.ids)
                                )
                                res.write({"event_ids": [(6, 0, new_event_ids)]})

            # Handle expense_ids
            if expense_ids and isinstance(expense_ids, list) and len(expense_ids) > 0:
                if isinstance(expense_ids[0], (list, tuple)) and len(expense_ids[0]) >= 3:
                    actual_expense_ids = expense_ids[0][2]
                    if actual_expense_ids:
                        existing_expenses = self.env["hr.expense"].browse(actual_expense_ids).filtered(
                            lambda e: e.community_id and e.community_id != res
                        )
                        if existing_expenses:
                            raise UserError(
                                _("The expense %s is attributed to an existing community.")
                                % existing_expenses[0].name
                            )
                        self.env["hr.expense"].browse(actual_expense_ids).write(
                            {"community_id": res.id}
                        )

        # Return the recordset as-is (not a list)
        return records

    def write(self, vals):
        res = super(BuCommunity, self).write(vals)

        employee_ids = vals.get("employee_ids")
        member_ids = vals.get("member_ids")
        expense_ids = vals.get("expense_ids")
        event_ids = vals.get("event_ids")

        # Handle employee_ids
        if employee_ids and isinstance(employee_ids, list) and len(employee_ids) > 0:
            if isinstance(employee_ids[0], (list, tuple)) and len(employee_ids[0]) >= 3:
                actual_employee_ids = employee_ids[0][2]
                if actual_employee_ids:
                    # Remove employees no longer in the list
                    removed_employees = self.employee_ids.filtered(lambda e: e.id not in actual_employee_ids)
                    removed_employees.write({"community_id": False})

                    # Check and add new employees
                    new_employees = self.env["hr.employee"].browse(actual_employee_ids).filtered(
                        lambda e: e.community_id != self
                    )
                    conflicting = new_employees.filtered(lambda e: e.community_id)
                    if conflicting:
                        raise UserError(
                            "The employee %s already belongs to an existing community."
                            % conflicting[0].name
                        )
                    new_employees.write({"community_id": self.id})

        # Handle member_ids
        if member_ids and isinstance(member_ids, list) and len(member_ids) > 0:
            if isinstance(member_ids[0], (list, tuple)) and len(member_ids[0]) >= 3:
                actual_member_ids = member_ids[0][2]
                if actual_member_ids:
                    # Remove members no longer in the list
                    removed_members = self.member_ids.filtered(lambda m: m.id not in actual_member_ids)
                    removed_members.write({"community_id": False})

                    # Check and add new members
                    new_members = self.env["res.partner"].browse(actual_member_ids).filtered(
                        lambda m: m.community_id != self
                    )
                    conflicting = new_members.filtered(lambda m: m.community_id)
                    if conflicting:
                        raise UserError(
                            "The member %s already belongs to an existing community."
                            % conflicting[0].name
                        )
                    new_members.write({"community_id": self.id})

        # Handle event_ids
        if event_ids and isinstance(event_ids, list) and len(event_ids) > 0:
            if isinstance(event_ids[0], (list, tuple)) and len(event_ids[0]) >= 3:
                actual_event_ids = event_ids[0][2]
                if actual_event_ids:
                    # Remove events no longer in the list
                    removed_events = self.event_ids.filtered(lambda e: e.id not in actual_event_ids)
                    removed_events.write({"community_id": False})

                    # Check and add new events
                    events_to_link = self.env["calendar.event"].browse(actual_event_ids)
                    new_events = events_to_link.filtered(lambda e: e.community_id != self)

                    conflicting = new_events.filtered(lambda e: e.community_id)
                    if conflicting:
                        raise UserError(
                            "The event %s is attributed to an existing community."
                            % conflicting[0].name
                        )

                    # Link new events and handle recurring events
                    for event in new_events:
                        event.write({"community_id": self.id})
                        if event.recurrency and event.recurrence_id:
                            recurring_events = event.recurrence_id.calendar_event_ids
                            recurring_events.write({"community_id": self.id})
                            # Update vals to include all recurring events
                            new_event_ids = list(set(actual_event_ids + recurring_events.ids))
                            vals["event_ids"] = [(6, 0, new_event_ids)]
                            res = super(BuCommunity, self).write(vals)

        # Handle expense_ids
        if expense_ids and isinstance(expense_ids, list) and len(expense_ids) > 0:
            if isinstance(expense_ids[0], (list, tuple)) and len(expense_ids[0]) >= 3:
                actual_expense_ids = expense_ids[0][2]
                if actual_expense_ids:
                    # Remove expenses no longer in the list
                    removed_expenses = self.expense_ids.filtered(lambda e: e.id not in actual_expense_ids)
                    removed_expenses.write({"community_id": False})

                    # Check and add new expenses
                    new_expenses = self.env["hr.expense"].browse(actual_expense_ids).filtered(
                        lambda e: e.community_id != self
                    )
                    conflicting = new_expenses.filtered(lambda e: e.community_id)
                    if conflicting:
                        raise UserError(
                            "The expense %s is attributed to an existing community."
                            % conflicting[0].name
                        )
                    new_expenses.write({"community_id": self.id})

        return res

    image = fields.Binary()

    stage = fields.Selection(
        selection=[
            ("new", "New"),
            ("operational", "Operational"),
        ],
        default="new",
        group_expand="_expand_states",
    )

    def action_open_community_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Community',
            'res_model': 'bu_community',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref(
                'bu_aha_communities.bu_community_form_view'
            ).id,
            'target': 'current',
        }

    def _expand_states(self, states, domain):
        return [key for key, val in type(self).stage.selection]

    # language = fields.Selection(
    #     selection=[
    #         ("english", "English"),
    #         ("spanish", "Spanish"),
    #         ("french", "French"),
    #         ("hebrew", "Hebrew"),
    #     ],
    #     required=True,
    #     default="english",
    # )

    @api.model
    def _lang_get(self):
        return self.env["res.lang"].get_installed()

    language = fields.Selection(_lang_get, string="Language")
    active_lang_count = fields.Integer(compute="_compute_active_lang_count")

    @api.depends("language")
    def _compute_active_lang_count(self):
        lang_count = len(self.env["res.lang"].get_installed())
        for partner in self:
            partner.active_lang_count = lang_count

    channel_id = fields.Many2one(
        string="Channel",
        comodel_name="discuss.channel",
        ondelete="restrict",
        required=True,
    )
    neighborhood = fields.Boolean()
    notes = fields.Text()
    email = fields.Char()
    city = fields.Char()
    phone = fields.Char()
    high_priority = fields.Boolean()
    sequence = fields.Integer()
    created_on = fields.Date(default=fields.Date.context_today)
    address = fields.Char()

    tag_ids = fields.Many2many(
        string="Tags",
        comodel_name="bu_community.tag",
    )
    responsible_id = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user
    )

    expense_ids = fields.Many2many(
        string="Expenses",
        comodel_name="hr.expense",
        # inverse_name="community_id",
        # domain=[("community_id", "=", False)],
    )

    # event_expenses_ids = fields.Many2many(
    #     string="Event Expenses",
    #     comodel_name="hr.expense",
    #     # inverse_name="community_id",
    #     # domain=[("community_id", "=", False)],

    # )

    event_ids = fields.Many2many(
        string="Events",
        comodel_name="calendar.event",
        # inverse_name="community_id",
        # domain=[("community_id", "=", False)],
    )

    def action_open_event_expenses(self):
        # data_obj = self.pool.get('ir.model.data')
        # tree_view_id = data_obj._get_id(cr, uid, 'project', 'view_project')
        return {
            "type": "ir.actions.act_window",
            "name": "All Expenses",
            "res_model": "hr.expense",
            # 'view_type' : 'tree',
            "domain": [
                "|",
                ("community_id", "=", self.id),
                ("event_id.community_id", "=", self.id),
            ],
            "view_mode": "list,form",
            "views": [
                (
                    self.env.ref(
                        "bu_aha_communities.bu_community_expense_all_tree_view"
                    ).id,
                    "list",
                ),
                (self.env.ref("hr_expense.hr_expense_view_form").id, "form"),
            ],
            # ref('bu_community_member_tree_view'
            # 'target':'current',
        }

    # def print_report(self):
    #     # data={
    #     #     'model':'bu_community',
    #     #     'form': self.read()[0]
    #     # }
    #     return self.env.ref("bu_aha_communities.report_community")
    # .with_context(landscape=True).report_action(self)

    # def go_to_channel(self):


class BuCommunityTag(models.Model):
    _name = "bu_community.tag"
    _description = "Bu Community Tag"  # TODO

    class Constraint(models.Constraint):
        _check_name_unique = ("unique (name)", "The name must be unique.")

    name = fields.Char(required=True)
    color = fields.Integer(default=4)


class BuCommunityStage(models.Model):
    _name = "bu_community.stage"
    _description = "Bu Community Stage"

    name = fields.Char(required=True)
    sequence = fields.Integer()
