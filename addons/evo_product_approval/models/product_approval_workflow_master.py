from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class ProductApprovalWorkflow(models.Model):
    _name = "product.approval.workflow.master"
    _rec_name = "name"
    _description = "Product Approval Master"

    name = fields.Char(string="Name", default='Product Approval Workflow')
    active_status = fields.Boolean(string='Active')
    approval_line_ids = fields.One2many('product.approval.lines', 'product_approval_id', string=' Product Approval Line')

    @api.constrains('active_status')
    def _check_active_status(self):
        record = self.search([('id', '!=', self.id), ('active_status', '=', True)])
        if len(record) > 0:
            raise ValidationError("There can be only 1 'active' Product Approval Workflow.")


class ProductApprovalLines(models.Model):
    _name = "product.approval.lines"
    _description = "Product approval lines description"

    product_approval_id = fields.Many2one('product.approval.workflow.master', string='Product Approval')
    job_position_id = fields.Many2one('hr.job', string="Job Position", required=True)
    approval_level = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third')
    ], string='Approval Level', required=True)
