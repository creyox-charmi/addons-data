from odoo import models, fields,api



class AddPage(models.Model):
    _inherit = 'purchase.order'


    approval_level_name = fields.Char(string="Approval Level",
                                 compute='_compute_approval_level_name')
    next_approval_level = fields.Integer(string="Next Approval Level",
                                         compute='_compute_next_approval_level')
    users = fields.Many2many(comodel_name='res.users',
                             string='Users',
                             compute='_compute_approval_info')
    groups = fields.Many2many(comodel_name='res.groups',
                              string='Groups',
                              compute='_compute_approval_info')
    reject_date = fields.Datetime(string='Reject Date')
    reject_by = fields.Many2one('res.users', string='Reject By')
    reject_reason = fields.Text(string='Reject Reason')
    level = fields.Integer(string='Level',default=1)
    approval_info_line_ids = fields.One2many(comodel_name='approval.info.line',
                                           inverse_name='purchase_order_id',
                                           string='approval_info_line_ids')
    is_boolean = fields.Boolean(
        string="Boolean", compute="compute_is_boolean", search='_search_is_boolean')

    def compute_is_boolean(self):

        if self.env.user.id in self.users.ids or any(
                item in self.env.user.groups_id.ids for item in self.groups.ids):
            self.is_boolean = True
        else:
            self.is_boolean = False

    @api.depends('amount_untaxed','amount_total')
    def _compute_approval_level_name(self):
       for record in self:
           # config_settings = self.env['ir.config_parameter'].sudo().get_param('conf_method')

           # gets the current company of the user.
           conf_method = record.env.user.company_id.conf_method

           if conf_method == 'untaxed_amount':
               print(conf_method)
               amounts_untaxed = []
               untaxed = record.amount_untaxed
               minimum_amounts = record.env['approval.configuration'].search(
                   [
                       ('minimum_amount', '<=', untaxed)
                   ]
               )

               if minimum_amounts:
                   if len(minimum_amounts) > 1:
                       for a in minimum_amounts:
                           amounts_untaxed.append(a.minimum_amount)

                       for m in minimum_amounts:
                           if m.minimum_amount == max(amounts_untaxed):
                               record.approval_level_name = m.name
                               # record.approval_info_line_ids.status = False
                               # record.approval_info_line_ids.approved_date = None
                               # record.approval_info_line_ids.approved_by = None


                   else:
                       record.approval_level_name = minimum_amounts.name
                       # record.approval_info_line_ids.status = False
                       # record.approval_info_line_ids.approved_date = None
                       # record.approval_info_line_ids.approved_by = None

               else:
                   record.approval_level_name='None'


           else:
               print(conf_method)
               amounts_total = []
               total = record.amount_total
               minimum_amounts = record.env['approval.configuration'].search(
                   [
                       ('minimum_amount', '<=', total)
                   ]
               )
               if minimum_amounts:
                   if len(minimum_amounts) > 1:
                       for a in minimum_amounts:
                           amounts_total.append(a.minimum_amount)

                       for m in minimum_amounts:
                           if m.minimum_amount == max(amounts_total):
                               record.approval_level_name = m.name
                               # record.approval_info_line_ids.status = False
                               # record.approval_info_line_ids.approved_date = None
                               # record.approval_info_line_ids.approved_by = None


                   else:
                       record.approval_level_name = minimum_amounts.name
                       # record.approval_info_line_ids.status = False
                       # record.approval_info_line_ids.approved_date = None
                       # record.approval_info_line_ids.approved_by = None


               else:
                   record.approval_level_name = 'None'


    @api.depends('level','approval_level_name')
    def _compute_next_approval_level(self):
        for record in self:
            record.next_approval_level = record.level if record.approval_level_name != 'None' else 0


    @api.depends('next_approval_level','approval_level_name')
    def _compute_approval_info(self):
        data = self.env['approval.configuration'].search(
            [
                ('name', '=', self.approval_level_name)
            ]
        )

        self.users = None
        self.groups = None

        for line in data.approval_details:
            if line.user_id and line.level == self.next_approval_level and line.approved_process_by == 'user':
                self.users = line.user_id

            if line.group_id and line.level == self.next_approval_level and line.approved_process_by == 'group':
                self.groups = line.group_id


    @api.onchange('approval_level_name')
    def add_info(self):
        for record in self:
            approval_config = record.env['approval.configuration'].search(
                [
                    ('name', '=', record.approval_level_name)
                ]
            )
            if approval_config:
                approval_line = approval_config.approval_details
                dict = []
                for line in approval_line:
                    dict.append((0, 0, {
                        'level': line.level,
                        'group_info': [(6, 0, line.group_id.ids)],
                        'user_info': [(6, 0, line.user_id.ids)],
                    }))
                self.update({
                    'approval_info_line_ids': dict
                })
            else:
                record.approval_info_line_ids = [(5, 0, 0)]



















