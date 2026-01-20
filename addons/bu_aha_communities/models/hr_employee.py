# Copyright 2022 Yves Goldberg (Ygol InternetWork)
# Part of module bu_aha_communities. See LICENSE file for
# full copyright and licensing details.

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    community_id = fields.Many2one("bu_community")
    has_community = fields.Boolean(default=False)
    community_position = fields.Selection(
        selection=[
            ("responsible", "Responsible"),
            ("worker", "Worker"),
        ],
        default="worker",
    )
    following_community_ids = fields.Many2many("bu_community", 'emp_members',
                                               "col1", "col2", store=True,
                                               compute="get_following_community")
    show_to_user = fields.Boolean(compute="get_user_visibility", store=True)
    following_community_employee_ids = fields.Many2many("hr.employee",
                                                     "emp_of_cms", "cm1",
                                                     "cm2",
                                                     store=True,
                                                     compute="get_following_community")

    @api.depends('following_community_employee_ids', 'following_community_ids')
    def get_user_visibility(self):
        user = self.env.user
        for rec in self:
            if user and rec.id in rec.following_community_employee_ids.ids:
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
                employee = []
                for i in community_ids:
                    for j in i.employee_ids:
                        employee.append(j.id)
                rec.following_community_employee_ids = [(6, 0, employee)]
            else:
                rec.following_community_ids = [(6, 0, [])]
                rec.following_community_employee_ids = [(6, 0, [])]
    # language = fields.Selection(
    #     selection=[
    #         ("english", "English"),
    #         ("spanish", "Spanish"),
    #         ("french", "French"),
    #         ("hebrew", "Hebrew"),
    #     ],
    #     default="english",
    # )

    @api.model
    def _lang_get(self):
        return self.env["res.lang"].get_installed()

    language = fields.Selection(_lang_get, string="Language")

    job_percentage = fields.Integer()
    monthly_salary = fields.Float()
    yearly_salary = fields.Float()

    _sql_constraints = [
        (
            "check_monthly_salary",
            "CHECK(monthly_salary >= 0)",
            "The monthly salary cannot be negative.",
        ),
        (
            "check_yearly_salary",
            "CHECK(yearly_salary >= 0)",
            "The yearly salary cannot be negative.",
        ),
        (
            "check_job_percentage",
            "CHECK(job_percentage >= 0)",
            "The job percentage cannot be negative.",
        ),
        (
            "check_job_percentage",
            "CHECK(job_percentage <= 100)",
            "The job percentage cannot be over 100.",
        ),
    ]

    @api.onchange(
        "monthly_salary"
    )  # this is onchange,self is the record, no need to iterate "for rec in self"
    def _onchange_monthly_salary(self):
        self.yearly_salary = self.monthly_salary * 12

    @api.onchange(
        "yearly_salary"
    )  # this is onchange,self is the record, no need to iterate "for rec in self"
    def _onchange_yearly_salary(self):
        if self.yearly_salary != 0:
            self.monthly_salary = self.yearly_salary / 12

    @api.model
    def create(self, vals_list):
        # Ensure vals_list is always a list (for backward compatibility)
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        res = super(HrEmployee, self).create(vals_list)

        # Process each record created
        for idx, vals in enumerate(vals_list):
            # Get the corresponding record
            record = res[idx] if len(vals_list) > 1 else res

            community_id = vals.get("community_id")

            if community_id:
                all_communities = self.env["bu_community"].search([])
                for community in all_communities:
                    if community.id == community_id:
                        id_list = []
                        for partner in community.employee_ids:
                            id_list.append(partner.id)
                        id_list.append(record.id)
                        community.write({"employee_ids": [[6, 0, id_list]]})

        return res

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
                 ('responsible_id', '=', self.env.user.id)]).mapped("employee_ids")

        if user.has_group('bu_aha_communities.bu_community_group_user'):
            domain = [('id', 'in', community_ids.ids)]
        if user.has_group('base.group_system') or manager:
            domain = []

        # for rec in community_ids:
        #     rec.community_id = rec.community_id.id
        return {
            'name': "Community Employees",
            'view_mode': 'list,form',
            'view_type': "form",
            'res_model': 'hr.employee',
            'target': 'self',
            'view_ids': [(False, 'list'),
                         (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': domain
        }

    # def write(self, vals):
    #     former = self.community_id
    #     res = super(HrEmployee, self).write(vals)
    #     community_id = vals.get("community_id")
    #     if former:
    #         id_list = []
    #         for partner in former.employee_ids:
    #             if partner.id != self.id:
    #                 id_list.append(partner.id)
    #         former.write({"employee_ids": [[6, 0, id_list]]})
    #     if not community_id:
    #         return res
    #     all_communities = self.env["bu_community"].search([])
    #     for community in all_communities:
    #         if community.id == community_id:
    #             id_list = [self.id]
    #             for partner in community.employee_ids:
    #                 id_list.append(partner.id)
    #             community.write({"employee_ids": [[6, 0, id_list]]})
    #     return res
