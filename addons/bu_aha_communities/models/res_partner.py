# Copyright 2022 Yves Goldberg (Ygol InternetWork)
# Part of module bu_aha_communities. See LICENSE file for
# full copyright and licensing details.

from odoo import api, fields, models,_
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # community_id = fields.Many2one("bu_aha_communities.bu_community")
    community_id = fields.Many2one("bu_community")
    # has_community = fields.Boolean(default=False)

    degree = fields.Selection(
        string="Degree",
        selection=[
            ("bachelors", "Bachelor's"),
            ("masters", "Master's"),
            ("doctoral", "Doctoral"),
        ],
    )
    degree_theme = fields.Selection(
        string="Degree Theme",
        selection=[
            ("arts", "Arts"),
            ("history", "History"),
            ("science", "Science"),
            ("religion", "Religion"),
        ],
    )
    dob = fields.Date(string="Date of birth")
    member_id_number = fields.Char(string="ID Number")
    aliyah_date = fields.Date(string="Date of Aliyah")
    moving_date = fields.Date(string="Arrival at city")
    # service_type = fields.Selection(
    #     string="Service",
    #     selection=[
    #         ("military", "Military"),
    #         ("national", "National"),
    #         ("civil", "Civil"),
    #     ],
    # )
    service = fields.Boolean(string="Military/National/Civil Service")
    reserve_service_status = fields.Selection(
        string="Reserve Service",
        selection=[("active", "Active"), ("inactive", "Inactive")],
    )
    joining_date = fields.Date(
        string="Joined Community", default=fields.Date.context_today
    )
    is_family = fields.Boolean(string="Family (children under 18)")
    activity_theme = fields.Text(string="Activity Theme")
    volunteer_hours = fields.Integer()
    project_name = fields.Text()
    country_of_origin = fields.Many2one("res.country")
    is_registration_summary = fields.Boolean(
        "Is there a registration summary?")
    has_signed_statement = fields.Boolean("Has signed a statement?")
    community_attachments = fields.Many2many("ir.attachment",
                                             "community_attachments",
                                             "partner", "attachment",
                                             compute="get_community_attachments")

    def find_consecutive_matches(self,str1, str2):
        if len(str1) < 7 or len(str2) < 7:
            return False

        for i in range(len(str1) - 6):
            if str1[i:i + 7] in str2:
                return True

        return False

    @api.depends('vat', 'company_id')
    def _compute_same_vat_partner_id(self):
        for partner in self:
            # use _origin to deal with onchange()
            partner_id = partner._origin.id
            #active_test = False because if a partner has been deactivated you still want to raise the error,
            #so that you can reactivate it instead of creating a new one, which would loose its history.
            Partner = self.with_context(active_test=False).sudo()
            partner.same_vat_partner_id = False
            # self.find_consecutive_matches(Partner.vat, self.vat)
            partners_vatlength = self.env['res.partner'].search([('id', '!=', Partner.id or Partner._origin.id), ('vat', '!=', False)]).filtered(
                lambda partner: len(partner.vat) >= 7)
            for partner_vat in partners_vatlength:
                if partner_vat.vat and Partner.vat:
                    if self.find_consecutive_matches(partner_vat.vat, Partner.vat):
                        domain = []
                        if partner.company_id:
                            domain += [('company_id', 'in', [False, partner.company_id.id])]
                        if partner_id:
                            domain += [('id', '!=', partner_id), '!', ('id', 'child_of', partner_id)]
                        partner.same_vat_partner_id = bool(partner.vat) and not partner.parent_id and Partner.search(domain, limit=1)

    @api.constrains("vat")
    def _check_vat(self):
        """A constrain to check the vat number is unique or not"""
        if self.vat and len(self.vat) >= 8 and not self.parent_id:
            if self.env['res.partner'].search([('id', '!=', self.id), ('vat', '=', self.vat), ('vat', '!=', False),('parent_id','=',False)]):
                raise UserError(_('A partner with the same vat {} already exists'.format(self.vat)))


    def get_community_attachments(self):
        for rec in self:
            attachments = self.env['ir.attachment'].search(
                [('res_id', '=', rec.id), ('res_model', '=', 'res.partner')])
            if attachments:
                rec.community_attachments = [(6, 0, attachments.ids)]
            else:
                rec.community_attachments = [(6, 0, attachments.ids)]

    @api.model
    @api.model
    def create(self, vals_list):
        # Ensure vals_list is always a list
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        res = super(ResPartner, self).create(vals_list)

        # Process each record
        for idx, vals in enumerate(vals_list):
            record = res[idx] if len(vals_list) > 1 else res
            community_id = vals.get("community_id")

            if community_id:
                # Find or get the "Community" tag
                community_tag = self.env["res.partner.category"].search(
                    [("name", "=", "Community")], limit=1
                )

                if community_tag:
                    # Get existing category_id values from vals or from the record
                    existing_tags = []
                    if "category_id" in vals and vals["category_id"]:
                        # Extract IDs from the Many2many command format
                        for cmd in vals["category_id"]:
                            if cmd[0] == 6:  # (6, 0, [ids])
                                existing_tags = cmd[2]
                            elif cmd[0] == 4:  # (4, id)
                                existing_tags.append(cmd[1])

                    # Add the Community tag if not already present
                    if community_tag.id not in existing_tags:
                        existing_tags.append(community_tag.id)
                        record.write({"category_id": [(6, 0, existing_tags)]})

                # Update the community's member_ids
                community = self.env["bu_community"].browse(community_id)
                if community.exists():
                    # Use the cleaner link command instead of replacing all IDs
                    community.write({"member_ids": [(4, record.id)]})

        return res

    # def write(self, vals):
    #     former = self.community_id
    #
    #     community_id = vals.get("community_id")
    #
    #     if community_id:
    #
    #         tags = self.env["res.partner.category"].search([])
    #         for tag in tags:
    #             if tag.name == "Community":
    #
    #                 # original_tag_list = vals.get("category_id")[0][2]
    #                 original_tag_list = vals.get("category_id")
    #                 if not original_tag_list:
    #                     original_tag_list = []
    #                 original_tag_list.append(tag.id)
    #                 # self.write({"category_id": [[6,0,original_tag_list]]})
    #                 # vals.append({"category_id": [[6,0,original_tag_list]]})
    #                 vals["category_id"] = [[6, 0, original_tag_list]]
    #
    #     res = super(ResPartner, self).write(vals)
    #     community_id = vals.get("community_id")
    #
    #     if former and community_id:
    #         id_list = []
    #         for partner in former.member_ids:
    #             if partner.id != self.id:
    #                 id_list.append(partner.id)
    #         former.write({"member_ids": [[6, 0, id_list]]})
    #     if not community_id:
    #         return res
    #     all_communities = self.env["bu_community"].search([])
    #     for community in all_communities:
    #         if community.id == community_id:
    #             id_list = [self.id]
    #             for partner in community.member_ids:
    #                 id_list.append(partner.id)
    #             community.write({"member_ids": [[6, 0, id_list]]})
    #
    #     # updated = all.search(['id','=',community_id])
    #     # updated = self.env["bu_community"].search(['id','=',community_id])
    #     # print(updated)
    #     # id_list = []
    #     # for partner in updated.member_ids:
    #     #     id_list.append(partner.id)
    #     # updated.write({'member_ids': [[6,0,id_list]]})
    #
    #     return res

    # @api.onchange("community_id")
    # def _onchange_community_id(self):
    #     if(self.community_id):
    #         category = self.env["res.partner.category"].search(['name','=','Community'])
    #         self.category_id = category.id
    #     else:
    #         self.category_id = False
    following_community_ids = fields.Many2many("bu_community", 'cm_members',
                                               "col1", "col2", store=True,
                                               compute="get_following_community")
    following_community_member_ids = fields.Many2many("res.partner",
                                                      "member_of_cms", "cm1",
                                                      "cm2",
                                                      store=True,
                                                      compute="get_following_community")
    show_to_user = fields.Boolean(compute="get_visibility_to_user", store=True)

    @api.depends('following_community_member_ids', 'following_community_ids')
    def get_visibility_to_user(self):
        user = self.env.user
        for rec in self:
            if user and rec.id in rec.following_community_member_ids.ids:
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
                members = []
                for i in rec.following_community_ids:
                    for j in i.member_ids:
                        members.append(j.id)
                rec.following_community_member_ids = [(6, 0, members)]
            else:
                rec.following_community_ids = [(6, 0, [])]
                rec.following_community_member_ids = [(6, 0, [])]

    def get_menu_action(self):
        user = self.env.user
        manager = user.has_group(
            "bu_aha_communities.bu_community_group_manager")
        domain = []

        community_ids = self.env['bu_community'].search(
            ['|', ('message_is_follower', '=', True),
             ('responsible_id', '=', self.env.user.id)]).mapped("member_ids")
        if user.has_group('bu_aha_communities.bu_community_group_user'):
            domain = [('id', 'in', community_ids.ids)]
        if user.has_group('base.group_system') or manager:
            domain = []


        # for rec in community_ids:
        #     rec.community_id = rec.community_id.id
        return {
            'name': "Community Members",
            'view_mode': 'list,form',
            'res_model': 'res.partner',
            'target': 'self',
            'view_ids': [(self.env.ref(
                'bu_aha_communities.bu_community_member_tree_view').id,
                          'list'),
                         (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': domain
        }
