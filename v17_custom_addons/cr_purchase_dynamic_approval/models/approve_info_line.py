from odoo import models, fields,api

class ApprovalInfo(models.Model):
    _name = 'approval.info.line'

    level = fields.Integer(string="Approval Level")
    user_info = fields.Many2many(comodel_name='res.users', string='Users', copy=True)
    group_info = fields.Many2many(comodel_name='res.groups',
                                  string='Groups',
                                  copy=True)
    status = fields.Boolean(string='Status')
    approved_date = fields.Datetime(string='Approved Date')
    approved_by = fields.Many2one('res.users', string='Approved By')
    purchase_order = fields.Char(string='Purchase Order')
    purchase_order_id = fields.Many2one('purchase.order')