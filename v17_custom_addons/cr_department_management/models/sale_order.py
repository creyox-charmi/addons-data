from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order'

    def action_open_wizard(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'split.sale.wizard',
            'views': [(False, 'form')],
            'target': 'new'
        }



