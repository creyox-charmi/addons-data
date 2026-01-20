from odoo import models, fields, api

class RejectWizard(models.TransientModel):
    _name = 'cr.reject.wizard'
    _description = 'Reject Wizard'

    reject_reason = fields.Text(string='Reject Reason')
    purchase_order_id = fields.Many2one(comodel_name = 'purchase.order',string='purchase_order_id')


    def action_confirm(self):
        print('confirm')
        print(self.purchase_order_id)
        try:
            self.purchase_order_id.write({
                'reject_date': fields.Datetime.now(),
                'reject_by': self.env.user.id,
                'reject_reason': self.reject_reason,
                'state':'reject'
            })
            print('Write operation successful.')
        except Exception as e:
            print(f"Error during write: {e}")


        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
