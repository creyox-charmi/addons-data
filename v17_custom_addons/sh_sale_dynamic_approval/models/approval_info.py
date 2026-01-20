from odoo import fields,models, _


class ApprovalInfo(models.Model):
    _inherit = 'sh.approval.info'
    _description = "Approval Information"

    sale_order_id = fields.Many2one('sale.order')
