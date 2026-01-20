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
            # Remove existing permanent NRE sub-lines
            wizard.sale_line_id.nre_sub_line_ids.unlink()

            # Create new permanent sub-lines from wizard lines
            for line in wizard.line_ids:
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

    # def action_create_invoice(self):
    #     """
    #     Create invoices for selected NRE sub-lines from the wizard.
    #
    #     Validations:
    #     - At least one sub-line must be selected.
    #     - Total billing percentage across all sub-lines must not exceed 100%.
    #     - Prevent invoicing a sub-line that is already invoiced.
    #     """
    #     self.ensure_one()
    #
    #     sale_line = self.sale_line_id
    #     order = sale_line.order_id
    #
    #     # --- Get selected wizard lines ---
    #     lines_to_process = self.line_ids.filtered(lambda l: l.selected)
    #     if not lines_to_process:
    #         raise UserError(_("Please select at least one sub-line to create invoice."))
    #
    #     # --- Validate billing percentage ---
    #     total_percentage = sum(l.billing_percentage for l in self.line_ids)
    #     if total_percentage > 100.0:
    #         raise UserError(_("Total Billing Percentage cannot exceed 100%%. Currently: %s") % total_percentage)
    #
    #     created_invoices = self.env['account.move']
    #
    #     for line in lines_to_process:
    #
    #         # --- Validation: Already invoiced ---
    #         if line.invoice_id:
    #             raise UserError(_("Sub-line %s is already invoiced (Invoice %s).")
    #                             % (line.sub_line_code, line.invoice_id.name))
    #
    #         # --- Find persistent NRE sub-line ---
    #         nre_line = self.env['sale.order.line.nre.sub'].search([
    #             ('sale_line_id', '=', sale_line.id),
    #             ('sub_line_code', '=', line.sub_line_code),
    #         ], limit=1)
    #         if not nre_line:
    #             raise UserError(_("Persistent NRE sub-line not found for %s") % line.sub_line_code)
    #
    #         # --- Compute billing amount ---
    #         billing_amount = line.billing_amount
    #
    #         # --- Create customer invoice ---
    #         invoice_vals = {
    #             'move_type': 'out_invoice',
    #             'partner_id': order.partner_id.id,
    #             'invoice_origin': order.name,
    #             'invoice_line_ids': [(0, 0, {
    #                 'product_id': line.product_id.id,
    #                 'name': line.sub_line_description or sale_line.name,
    #                 'quantity': 1,
    #                 'price_unit': billing_amount,
    #                 'sale_line_ids': [(6, 0, [sale_line.id])],
    #             })],
    #         }
    #         invoice = self.env['account.move'].create(invoice_vals)
    #         created_invoices |= invoice
    #
    #         # --- Link invoice to wizard line & permanent sub-line ---
    #         line.invoice_id = invoice.id
    #         line.invoicing_status = 'invoiced'
    #         nre_line.write({
    #             'invoice_id': invoice.id,
    #             'invoicing_status': 'invoiced',
    #             'invoiced_amount': billing_amount,
    #         })
    #
    #     # --- Update remaining invoicing amount on main SO line ---
    #     total_invoiced = sum(
    #         nre_line.invoiced_amount
    #         for nre_line in self.env['sale.order.line.nre.sub']
    #             .search([('sale_line_id', '=', sale_line.id)])
    #     )
    #     sale_line.nre_remaining_amount = sale_line.price_unit - total_invoiced
    #
    #     # --- Return action to open the first created invoice ---
    #     if created_invoices:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'account.move',
    #             'view_mode': 'form',
    #             'res_id': created_invoices[0].id,
    #             'target': 'current',
    #         }
    #
    #     return True

    def action_create_invoice(self):
        """
        Create invoices for selected NRE sub-lines from the wizard using standard down-payment flow.
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

        created_invoices = self.env['account.move']

        for line in lines_to_process:
            print('line : ',line)
            print('pn ',line.everest_pn)

            # --- Already invoiced check ---
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

            if not order or not order.exists():
                raise UserError(_("Sale Order not found or not saved - cannot create invoice."))

            # --- Create advance payment wizard for this sub-line ---
            adv_wizard = self.env['sale.advance.payment.inv'].create({
                'advance_payment_method': 'percentage',
                'amount': line.billing_percentage or 0.0,
                'sale_order_ids': [(6, 0, [order.id])],
            })

            # --- Create invoice using standard flow ---
            invoices = adv_wizard.with_context(force_new_invoice=True)._create_invoices(adv_wizard.sale_order_ids)
            if not invoices:
                continue

            # --- Usually only one invoice per sub-line ---
            invoice = invoices[0]
            created_invoices |= invoice

            # --- Find down-payment invoice lines ---
            dp_lines = invoice.line_ids.filtered(
                lambda il: getattr(il, 'is_downpayment', False)
                           or (il.sale_line_ids and any(
                    getattr(sl, 'is_downpayment', False) for sl in il.sale_line_ids))
            )
            if not dp_lines:
                # fallback by price_unit match
                dp_lines = invoice.line_ids.filtered(
                    lambda il: float_compare(il.price_unit, line.billing_amount, 2) == 0)

            # --- Compute tax-inclusive total ---
            invoiced_total = sum(dp_line.price_total or 0.0 for dp_line in dp_lines) or \
                             sum(l.price_total or 0.0 for l in invoice.line_ids if not l.display_type)

            # --- Update wizard line and persistent sub-line ---
            line.invoice_id = invoice.id
            line.invoicing_status = 'invoiced'

            nre_vals = {
                'invoice_id': invoice.id,
                'invoicing_status': 'invoiced',
            }
            if 'invoiced_amount' in nre_line._fields:
                nre_vals['invoiced_amount'] = invoiced_total
            nre_line.write(nre_vals)

        # --- Update remaining invoicing amount on main SO line ---
        taxes_res = sale_line.tax_id.compute_all(
            sale_line.price_unit * (1 - (sale_line.discount or 0.0) / 100.0),
            order.currency_id,
            sale_line.product_uom_qty,
            product=sale_line.product_id,
            partner=order.partner_id,
        )
        total_with_tax = taxes_res.get('total_included', sale_line.price_subtotal)

        total_invoiced = sum(
            sub.invoiced_amount for sub in
            self.env['sale.order.line.nre.sub'].search([('sale_line_id', '=', sale_line.id)])
            if getattr(sub, 'invoiced_amount', False)
        )
        sale_line.nre_remaining_amount = max(total_with_tax - (total_invoiced or 0.0), 0.0)

        # --- Return action to open the first created invoice (if any) ---
        if created_invoices:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': created_invoices[0].id,
                'target': 'current',
            }

        return True








