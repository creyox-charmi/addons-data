# Copyright 2022 Yves Goldberg (Ygol InternetWork)
# Part of module bu_aha_communities. See LICENSE file for
# full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    community_id = fields.Many2one("bu_community")
    event_id = fields.Many2one("calendar.event")
    related_to = fields.Selection(
        string="Related To",
        selection=[
            ("community", "Community (General)"),
            ("event", "Community (Event)"),
        ],
    )
    expense_provider = fields.Char("Expense Provider Name")
    expense_receipt = fields.Char("Expense Receipt Number")
    expense_receipt_date = fields.Date("Expense Receipt Date")
    receipt_date = fields.Date("Receipt Date")

    @api.onchange('expense_receipt')
    def _onchange_partner_name(self):
        """To check the length of expence_receipt and raise error"""
        if self.expense_receipt:
            if len(self.expense_receipt) > 7:
                raise UserError(_('Please write only 7 characters.'))

    @api.onchange(
        "related_to"
    )  # self is the record and no need to iterate "for rec in self"
    def _onchange_related_to(self):
        if self.related_to:
            if self.related_to == "community":
                self.event_id = False
            if self.related_to == "event":
                self.community_id = False
        else:
            self.community_id = False
            self.event_id = False

    @api.model
    def create(self, vals_list):
        # Ensure vals_list is always a list
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        res = super(HrExpense, self).create(vals_list)

        # Process each record created
        for idx, vals in enumerate(vals_list):
            # Get the corresponding record
            record = res[idx] if len(vals_list) > 1 else res

            community_id = vals.get("community_id")
            event_id = vals.get("event_id")

            if community_id:
                all_communities = self.env["bu_community"].search([])
                for community in all_communities:
                    if community.id == community_id:
                        id_list = []
                        for partner in community.expense_ids:
                            id_list.append(partner.id)
                        id_list.append(record.id)
                        community.write({"expense_ids": [[6, 0, id_list]]})

            if event_id:
                all_events = self.env["calendar.event"].search([])
                for event in all_events:
                    if event.id == event_id:
                        id_list = []
                        for ev in event.expense_ids:
                            id_list.append(ev.id)
                        id_list.append(record.id)
                        event.write({"expense_ids": [[6, 0, id_list]]})

        return res

    # def write(self, vals):
    #     former = self.community_id
    #     formerEvent = self.event_id
    #
    #     res = super(HrExpense, self).write(vals)
    #     community_id = vals.get("community_id")
    #     if former:
    #         id_list = []
    #         for partner in former.expense_ids:
    #             if partner.id != self.id:
    #                 id_list.append(partner.id)
    #         former.write({"expense_ids": [[6, 0, id_list]]})
    #     if community_id:
    #         all = self.env["bu_community"].search([])
    #         for community in all:
    #             if community.id == community_id:
    #                 id_list = [self.id]
    #                 for partner in community.expense_ids:
    #                     id_list.append(partner.id)
    #                 community.write({"expense_ids": [[6, 0, id_list]]})
    #
    #     event_id = vals.get("event_id")
    #     if formerEvent:
    #         id_list = []
    #         for exp in formerEvent.expense_ids:
    #             if exp.id != self.id:
    #                 id_list.append(exp.id)
    #         formerEvent.write({"expense_ids": [[6, 0, id_list]]})
    #     if event_id:
    #         all = self.env["calendar.event"].search([])
    #         for event in all:
    #             if event.id == event_id:
    #                 id_list = [self.id]
    #                 for partner in event.expense_ids:
    #                     id_list.append(partner.id)
    #                 event.write({"expense_ids": [[6, 0, id_list]]})
    #
    #     return res

    following_community_ids = fields.Many2many("bu_community", 'cm_expenses',
                                               "col1", "col2", store=True,
                                               compute="get_following_community")
    following_community_exp_ids = fields.Many2many("hr.expense",
                                                      "expense_of_cms", "cm1",
                                                      "cm2",
                                                      store=True,
                                                      compute="get_following_community")
    show_to_user = fields.Boolean(compute="get_visibility_to_user", store=True)

    @api.depends('following_community_exp_ids', 'following_community_ids')
    def get_visibility_to_user(self):
        user = self.env.user
        for rec in self:
            if user and rec.id in rec.following_community_exp_ids.ids:
                rec.show_to_user = True
                print("\n\n-----------Show to User", rec.show_to_user, rec)
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
                exps = []
                for i in rec.following_community_ids:
                    for j in i.expense_ids:
                        exps.append(j.id)
                rec.following_community_exp_ids = [(6, 0, exps)]
            else:
                rec.following_community_ids = [(6, 0, [])]
                rec.following_community_exp_ids = [(6, 0, [])]

    def get_menu_action(self):
        user = self.env.user
        manager = user.has_group(
            "bu_aha_communities.bu_community_group_manager")
        domain = []
        if manager:
            domain.append(('community_id', '!=', False))
        else:
            domain.append(('show_to_user', '=', True))

        community_ids = self.env['bu_community'].search(['|', ('message_is_follower', '=', True),
                 ('responsible_id', '=', self.env.user.id)]).mapped("expense_ids")

        if user.has_group('bu_aha_communities.bu_community_group_user'):
            domain = [('id', 'in', community_ids.ids)]
        if user.has_group('base.group_system') or manager:
            domain = []

        # for rec in community_ids:
        #     rec.community_id = rec.community_id.id
        return {
            'name': "Community Expenses",
            'view_mode': 'list,form',
            'res_model': 'hr.expense',
            'target': 'self',
            'view_ids': [(self.env.ref(
                'bu_aha_communities.bu_community_expense_tree_view').id,
                          'list'),
                         (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': domain
        }


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense"

    def approve_expense_sheets(self):
        for rec in self:   # added for loop to avoid singleton errors
            if rec.attachment_number == 0:
                raise UserError(_("There is no document attached."))
            else:
                return super(HrExpenseSheet, self).approve_expense_sheets()
