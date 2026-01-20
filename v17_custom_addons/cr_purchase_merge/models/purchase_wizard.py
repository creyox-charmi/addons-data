from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseWizard(models.TransientModel):
    _name = 'purchase.wizard'

    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string="Customer",
                                 require=True)

    purchase_id = fields.Many2one(comodel_name='purchase.order',
                                    string='Purchase')

    merge_type = fields.Selection(
        [
            ('Do_Nothing','Do Nothing'),
            ('Cancel_Other_RFQ','Cancel Other RFQ'),
            ('Remove_Other_RFQ','Remove Other RFQ')
        ],
        string='Merge Type'
    )

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        purchase_tick = self.env['purchase.order'].browse(self._context.get('active_ids'))

        if len(purchase_tick) < 2:
            raise UserError("Must be select 2 or more row!")

        for p in purchase_tick:
            if p.state == 'draft' or p.state == 'sent' or p.state == 'cancel':
                pass
            else:
                raise UserError("Must be in 'RFQ' or 'RFQ Sent' stat")


        return result



    def action_merge(self):
        purchase_tick = self.env['purchase.order'].browse(self._context.get('active_ids'))

        if self.purchase_id:
            new_order = self.purchase_id
        else:
            new_order = self.env['purchase.order'].create({
                'partner_id': self.partner_id.id,
                'date_order': fields.Datetime.now(),
            })

        for p in purchase_tick:
            for line in p.order_line:
                line.copy({'order_id':new_order.id})

        if self.merge_type == 'Cancel_Other_RFQ':
            for b in purchase_tick:
                if self.purchase_id != b:
                    b.button_cancel()

        if self.merge_type == 'Remove_Other_RFQ':
            for b in purchase_tick:
                if self.purchase_id != b:
                    b.unlink()


        return {'type': 'ir.actions.act_window_close'}




    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
