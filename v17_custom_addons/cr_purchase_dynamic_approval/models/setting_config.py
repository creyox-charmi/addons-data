from odoo import models, fields

class SettingConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company')
    conf_method = fields.Selection(string='Approved Based On',related="company_id.conf_method",readonly=False)





