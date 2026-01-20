# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderLineNRESubWizard(models.TransientModel):
    _name = 'sale.order.line.nre.sub.wizard'
    _description = 'Wizard for NRE Sub-lines'

    sale_line_id = fields.Many2one('sale.order.line', required=True)
    line_ids = fields.One2many('sale.order.line.nre.sub.wizard.line', 'wizard_id')


    def action_confirm(self):
        """
        Confirm changes from the wizard and push wizard lines
        into permanent sub-lines (sale.order.line.nre.sub).
        """
        for wizard in self:
            # Only delete non-invoiced sub-lines
            wizard.sale_line_id.nre_sub_line_ids.filtered(
                lambda s: s.invoicing_status != 'invoiced'
            ).unlink()

            # Get existing invoiced sub-lines
            existing_invoiced = {
                sub.everest_pn: sub
                for sub in wizard.sale_line_id.nre_sub_line_ids
            }

            # Create or skip sub-lines
            for line in wizard.line_ids:
                # Skip if this sub-line is already invoiced
                if line.everest_pn in existing_invoiced:
                    continue

                self.env['sale.order.line.nre.sub'].create({
                    'sale_line_id': wizard.sale_line_id.id,
                    'everest_pn': line.everest_pn,
                    'product_id': line.product_id.id,
                    'billing_percentage': line.billing_percentage,
                    'sub_line_description': line.sub_line_description,
                    'sub_line_code': line.sub_line_code,
                    'required_delivery_date': line.required_delivery_date,
                    'updated_delivery_date': line.updated_delivery_date,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line.nre.sub.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_invoice(self):
        """
        Create fixed invoices (not down payment type) for selected NRE sub-lines.
        Invoice amount is based on billing_percentage of the product price.
        """
        self.ensure_one()
        sale_line = self.sale_line_id
        order = sale_line.order_id


        # --- Get selected wizard lines ---
        lines_to_process = self.line_ids.filtered(lambda l: l.selected)

        if not lines_to_process:
            raise UserError(_("Please select at least one sub-line to create invoice."))

        # --- Validate billing percentage ---
        total_percentage = sum(l.billing_percentage for l in self.line_ids)

        if total_percentage > 100.0:
            raise UserError(_("Total Billing Percentage cannot exceed 100%%. Currently: %s") % total_percentage)

        invalid_lines = lines_to_process.filtered(lambda l: not l.billing_percentage or l.billing_percentage <= 0)
        if invalid_lines:
            raise UserError(_(
                "Billing Percentage must be greater than 0 for all selected lines.\n"
                "Invalid Lines: %s"
            ) % ', '.join(invalid_lines.mapped('everest_pn')))

        created_invoices = self.env['account.move']

        for line in lines_to_process:

            if line.invoice_id:
                raise UserError(_("Sub-line %s is already invoiced (Invoice %s).")
                                % (line.sub_line_code, line.invoice_id.name))

            # --- Find persistent NRE sub-line ---
            nre_line = self.env['sale.order.line.nre.sub'].search([
                ('sale_line_id', '=', sale_line.id),
                ('everest_pn', '=', line.everest_pn),
            ], limit=1)


            if not nre_line:
                raise UserError(_("Persistent NRE sub-line not found for %s") % line.sub_line_code)

            # --- Compute amount based on billing percentage ---
            base_price = sale_line.price_unit * sale_line.product_uom_qty
            percentage = line.billing_percentage or 0.0
            price = (base_price * percentage) / 100.0

            # --- Create invoice manually (fixed invoice) ---
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': order.partner_id.id,
                'invoice_origin': order.name,
                'invoice_line_ids': [(0, 0, {
                    'name': f"NRE Sub-Line: {line.everest_pn or ''} ({percentage}%)",
                    'product_id': sale_line.product_id.id,
                    'quantity': 1,
                    'price_unit': price,
                    'tax_ids': [(6, 0, sale_line.tax_id.ids)],
                    'sale_line_ids': [(6, 0, [sale_line.id])],
                })],
                'invoice_payment_term_id': order.payment_term_id.id,
                'currency_id': order.currency_id.id,
                'invoice_date': fields.Date.context_today(self),
            }

            invoice = self.env['account.move'].create(invoice_vals)

            created_invoices |= invoice

            # --- Update wizard line and NRE sub-line ---
            line.invoice_id = invoice.id
            line.invoicing_status = 'invoiced'

            nre_line.write({
                'invoice_id': invoice.id,
                'invoicing_status': 'invoiced',
                'invoiced_amount': price,
            })

        # --- Update remaining invoicing amount on main SO line ---
        total_with_tax = sale_line.price_total
        total_invoiced = sum(
            sub.invoiced_amount for sub in
            self.env['sale.order.line.nre.sub'].search([('sale_line_id', '=', sale_line.id)])
            if getattr(sub, 'invoiced_amount', False)
        )
        sale_line.nre_remaining_amount = max(total_with_tax - (total_invoiced or 0.0), 0.0)


        # --- Return action to open the first created invoice ---
        if created_invoices:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': created_invoices[0].id,
                'target': 'current',
            }

        return True











