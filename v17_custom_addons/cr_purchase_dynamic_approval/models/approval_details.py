from email.policy import default

from odoo import api, fields, models, _

class ApprovalConfiguration(models.Model):
    _name = 'approval.details'


    approved_process_by = fields.Selection([
                                               ('user', 'User'),
                                               ('group', 'Group')
                                           ],
                                           string="Approved Process By",
                                            default='user'
                                           )
    level = fields.Integer(string='Level')
    approved_id = fields.Many2one(comodel_name='approval.configuration',
                                  string="approved_id")

    user_id = fields.Many2many(comodel_name='res.users',copy=False)
    group_id = fields.Many2many(comodel_name='res.groups',
                                string = 'Group Name',
                                copy=False)

