from odoo import api, fields, models, _

class ApprovalConfiguration(models.Model):
    _name = 'approval.configuration'


    name = fields.Char(string="name")
    minimum_amount = fields.Float(string='Minimum Amount',required=True)
    company_ids = fields.Many2many(comodel_name='res.company',
                                       string='Allowed Companies',default=lambda self: self.env.company)
    user_always_in_cc = fields.Boolean(string="USer Always in CC")
    approval_details = fields.One2many(comodel_name='approval.details',
                                        inverse_name='approved_id',
                                        string="Approval Details")
