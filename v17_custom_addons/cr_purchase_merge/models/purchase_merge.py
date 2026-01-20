from odoo import api, fields, models, _

class CopyLines(models.Model):
    _inherit = 'purchase.order'

    def action_open_wizard_purchase(self):

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.wizard',
            'views': [(False, 'form')],
            'target': 'new'
        }