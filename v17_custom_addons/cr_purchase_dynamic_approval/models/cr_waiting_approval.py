from odoo import api, fields, models, _

class CrWaitingApproval(models.Model):
    _inherit = 'purchase.order'