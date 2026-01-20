from odoo import api, fields, models, _

class CopyLines(models.Model):
    _inherit = 'account.move.line'

    def invoicing_copy_line(self):
        for record in self:
            record.copy(
                {'product_id': record.product_id.id}
            )
