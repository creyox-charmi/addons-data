from odoo import models, fields, api

class NRESubLineWizard(models.TransientModel):
    """Wizard for managing NRE sub-lines with milestone billing"""
    _name = 'sale.order.line.nre.sub.wizard'
    _description = 'NRE Sub-line Wizard'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string="Sale Order Line",
        required=True,
    )

    line_ids = fields.One2many(
        'sale.order.line.nre.sub.wizard.line',
        'wizard_id',
        string="Sub Lines"
    )

    def action_confirm(self):
        """Confirm wizard and create/update sub-lines"""
        self.ensure_one()
        for line in self.line_ids:
            self.env['sale.order.line.nre.sub'].create({
                'sale_line_id': self.sale_line_id.id,
                'everest_pn': line.everest_pn,
                'product_id': line.product_id.id,
                'billing_percentage': line.billing_percentage,
                'sub_line_description': line.sub_line_description,
                'sub_line_code': line.sub_line_code,
                'required_delivery_date': line.required_delivery_date,
                'updated_delivery_date': line.updated_delivery_date,
            })
        return {'type': 'ir.actions.act_window_close'}

    def action_create_invoice(self):
        """Create invoice from wizard sub-lines"""
        self.ensure_one()
        order = self.sale_line_id.order_id

        # compute total amount for all wizard lines
        invoice_lines = []
        for line in self.line_ids:
            amount = (self.sale_line_id.price_unit * line.billing_percentage) / 100.0
            invoice_lines.append((0, 0, {
                'product_id': line.product_id.id or self.sale_line_id.product_id.id,
                'name': line.sub_line_description or self.sale_line_id.name,
                'quantity': 1,
                'price_unit': amount,
                'sale_line_ids': [(6, 0, [self.sale_line_id.id])],
            }))

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': order.partner_id.id,
            'invoice_origin': order.name,
            'invoice_line_ids': invoice_lines,
        })

        return {
            'name': 'Customer Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }