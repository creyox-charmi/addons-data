from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approve'),
        ('reject', 'Reject')
    ], default='draft', string='Status')
    product_approval_history_ids = fields.One2many('product.approval.history', 'product_approval_hist_id',
                                                   string='Product Approval Status')
    related_users_ids = fields.Many2many('res.users', string="Related Users")
    contact_partner_id = fields.Char('Contact Partner ID')
    active = fields.Boolean(string='Active', default=False)
    user_approve_boolean = fields.Boolean('User Approved', compute='check_for_user_approve')

    @api.depends('state', 'related_users_ids', 'product_approval_history_ids')
    def check_for_user_approve(self):
        user_id = self.env.user.id
        for rec in self:
            user_approve_boolean = False
            if rec.related_users_ids:
                allow_user = rec.related_users_ids.filtered(lambda r: r.id == user_id)
                if not allow_user:
                    user_approve_boolean = False
                else:
                    user_approve_boolean = True
            rec.update({
                'user_approve_boolean': user_approve_boolean
            })

    def action_send_approval(self):

        statuses = self.env['product.approval.workflow.master'].search([('active_status', '=', True)], limit=1)
        admin_user_data = self.env['hr.employee'].search([])
        if not statuses:
            raise ValidationError(_("No product approval workflow available"))
        elif statuses and not statuses.approval_line_ids:
            raise ValidationError(_("Product approval workflow is not configured"))
        else:
            for status in statuses:
                self.state = 'pending'
                if len(status.approval_line_ids) == 1:
                    for lines in status.approval_line_ids:
                        admin_user_data_position = self.env['hr.employee'].search(
                            [('job_id', '=', lines.job_position_id.id)])
                        for employee in admin_user_data_position:
                            if employee.user_id:
                                self.related_users_ids = [(4, employee.user_id.id)]
                elif len(status.approval_line_ids) == 2:
                    level_1 = status.approval_line_ids.filtered(lambda x: x.approval_level == 'first')
                    level_2 = status.approval_line_ids.filtered(lambda x: x.approval_level == 'second')
                    if level_1:
                        admin_user_data_position = self.env['hr.employee'].search(
                            [('job_id', '=', level_1.job_position_id.id)])
                        for employee in admin_user_data_position:
                            if employee.user_id:
                                self.related_users_ids = [(4, employee.user_id.id)]
                    elif level_2 and not level_1:
                        admin_user_data_position = self.env['hr.employee'].search(
                            [('job_id', '=', level_2.job_position_id.id)])
                        for employee in admin_user_data_position:
                            if employee.user_id:
                                self.related_users_ids = [(4, employee.user_id.id)]
                else:
                    for lines in status.approval_line_ids:
                        if lines.approval_level == 'first':
                            admin_user_data_position = self.env['hr.employee'].search(
                                [('job_id', '=', lines.job_position_id.id)])
                            for employee in admin_user_data_position:
                                if employee.user_id:
                                    self.related_users_ids = [(4, employee.user_id.id)]
                        # elif lines.approval_level == 'second':
                        #     print('------- if level 1 approved . then level 2 ka many to many ')
                        # else:
                        #     print('------- if level 1,2 approved . then level 3 ka many to many ')

    def action_reset_to_draft(self):
        self.state = 'draft'


    def write(self, vals):
        if 'default_code' in vals or 'name' in vals:
            if self.state == 'pending':
                vals.update({
                    'state': 'draft',
                    'related_users_ids': [(5, 0, 0)],
                })
        return super(ProductTemplate, self).write(vals)

class ProductApprovalHistory(models.Model):
    _name = "product.approval.history"
    _description = "Product Approval History Record"

    product_approval_hist_id = fields.Many2one("product.template")
    approved_by = fields.Char(string="User")
    approved_on = fields.Datetime(string='Date')
    approval_reason = fields.Char(string="Reason ")
    approved_rejected = fields.Char(string='Status')
    level_admin_user = fields.Char(string='User Level')