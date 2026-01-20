from datetime import datetime

from odoo import api, fields, models, _

class CrMyApproval(models.Model):
    _inherit = 'purchase.order'

    def action_approve(self):
        print("approve")

        for record in self:
            for line in record.approval_info_line_ids:
                if line.level == record.next_approval_level and line.status == False:
                    line.status = True
                    line.approved_date = fields.Datetime.now()
                    line.approved_by = record.env.user.id


            flag = False

            for line in record.approval_info_line_ids:
                next_level = record.next_approval_level + 1
                if line.level == next_level and line.status == False:
                    flag = True

            if flag == True:
                record.level = record.level + 1
            else:
                record.level = 0
                record.write({'state': 'purchase'})



    def action_reject(self):
        print("action_reject")
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cr.reject.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context':{'default_purchase_order_id':self.id}
        }

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})