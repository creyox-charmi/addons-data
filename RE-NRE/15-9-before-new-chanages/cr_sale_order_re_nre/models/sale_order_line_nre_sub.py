# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api

class SaleOrderLineNRESub(models.Model):
    _name = 'sale.order.line.nre.sub'
    _description = 'Sale Order Line NRE Sub Lines'
    _order = 'sale_line_id, sequence, id'

    sale_line_id = fields.Many2one('sale.order.line', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    everest_pn = fields.Char(required=True)
    product_id = fields.Many2one('product.product', required=True)
    billing_percentage = fields.Float()
    sub_line_description = fields.Text()
    sub_line_code = fields.Char()
    required_delivery_date = fields.Date()
    updated_delivery_date = fields.Date()

    billing_amount = fields.Float(compute='_compute_billing_amount', store=True)
    invoice_id = fields.Many2one("account.move", string="Invoice")
    invoicing_status = fields.Selection([
        ("to_invoice", "To Invoice"),
        ("invoiced", "Invoiced"),
    ], string="Invoicing Status", default="to_invoice")
    invoiced_amount = fields.Monetary(string="Invoiced Amount", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", related="sale_line_id.currency_id", store=True)


    @api.depends('billing_percentage', 'sale_line_id.price_subtotal')
    def _compute_billing_amount(self):
        """
        Compute billing amount for each sub-line based on:
        (Billing Percentage * Sale Order Line Subtotal) / 100
        """
        for rec in self:
            rec.billing_amount = (rec.billing_percentage / 100.0) * rec.sale_line_id.price_subtotal

    def action_create_invoice(self):
        """
        Create customer invoices for selected milestone(s).

        - Skips already invoiced sub-lines.
        - Creates an invoice with product, description, and computed billing amount.
        - Links the generated invoice to the sub-line and updates invoicing status.
        - Returns an action to open the created invoice form.
        """
        moves = []
        for sub in self:
            if sub.invoicing_status == 'invoiced':
                continue  # Skip already invoiced milestones

            # Create invoice
            move = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': sub.sale_line_id.order_id.partner_id.id,
                'invoice_origin': sub.sale_line_id.order_id.name,
                'invoice_line_ids': [(0, 0, {
                    'product_id': sub.product_id.id,
                    'name': sub.sub_line_description or sub.everest_pn,
                    'quantity': 1,
                    'price_unit': sub.billing_amount,
                    'sale_line_ids': [(6, 0, [sub.sale_line_id.id])],
                })]
            })
            moves.append(move)

            # Update invoicing status on sub-line
            sub.write({
                'invoiced_amount': sub.billing_amount,
                'invoicing_status': 'invoiced',
            })

        # Return action to open the first created invoice
        return {
            'name': 'Customer Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': moves[0].id if moves else False,
        }