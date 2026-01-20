# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLineRESubWizard(models.TransientModel):
    _name = 'sale.order.line.re.sub.wizard'
    _description = 'Wizard for RE Sub-lines'

    sale_line_id = fields.Many2one('sale.order.line', required=True)
    line_ids = fields.One2many('sale.order.line.re.sub.wizard.line', 'wizard_id', string="RE Sub-lines")

    def action_confirm(self):
        """
        Confirm changes from the wizard and push wizard lines
        into permanent RE sub-lines (sale.order.line.re.sub).
        """
        for wizard in self:
            # Remove existing permanent RE sub-lines
            wizard.sale_line_id.re_sub_line_ids.unlink()

            # Create new permanent sub-lines from wizard lines
            for line in wizard.line_ids:
                self.env['sale.order.line.re.sub'].create({
                    'sale_line_id': wizard.sale_line_id.id,
                    'everest_pn': line.everest_pn,
                    'quantity': line.quantity,
                    'qty_delivered': line.qty_delivered,
                    'remaining_qty_to_deliver': line.remaining_qty_to_deliver,
                    'required_delivery_date': line.required_delivery_date,
                    'updated_delivery_date': line.updated_delivery_date,
                    'sub_line_code': line.sub_line_code,
                })
        return True
