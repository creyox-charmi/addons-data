import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrderLineNRESubWizard(models.TransientModel):
    _name = 'sale.order.line.nre.sub.wizard'
    _description = 'Wizard for NRE Sub-lines'

    sale_line_id = fields.Many2one('sale.order.line', required=True)
    line_ids = fields.One2many('sale.order.line.nre.sub.wizard.line', 'wizard_id')

    def action_confirm(self):
        """Push wizard lines into permanent sub-lines"""
        for wizard in self:
            wizard.sale_line_id.nre_sub_line_ids.unlink()
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
    #     self.ensure_one()
    #     _logger.info(">>> Action Create Invoice triggered for sale_line_id %s", self.sale_line_id.id)
    #
    #     sale_line = self.sale_line_id
    #     order = sale_line.order_id
    #
    #     # --- Validation: billing % cannot exceed 100 ---
    #     total_percentage = sum(l.billing_percentage for l in self.line_ids)
    #     _logger.info(">>> Current total billing percentage: %s", total_percentage)
    #     if total_percentage > 100.0:
    #         raise UserError(_("Total Billing Percentage cannot exceed 100%%. Currently: %s") % total_percentage)
    #
    #     created_invoices = self.env['account.move']
    #
    #     for line in self.line_ids:
    #         _logger.info(">>> Processing wizard line %s with code %s", line.id, line.sub_line_code)
    #
    #         # --- Validation: already invoiced ---
    #         if line.invoice_id:
    #             raise UserError(_("Sub-line %s is already invoiced (Invoice %s).")
    #                             % (line.sub_line_code, line.invoice_id.name))
    #
    #         # Find persistent sub-line
    #         nre_line = self.env['sale.order.line.nre.sub'].search([
    #             ('sale_line_id', '=', sale_line.id),
    #             ('sub_line_code', '=', line.sub_line_code),
    #         ], limit=1)
    #
    #         if not nre_line:
    #             raise UserError(_("Persistent NRE sub-line not found for %s") % line.sub_line_code)
    #
    #         # Calculate billing amount
    #         billing_amount = (sale_line.price_unit * line.billing_percentage) / 100.0
    #         _logger.info(">>> Creating invoice for billing_amount %s", billing_amount)
    #
    #         # Create invoice
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
    #         # Link invoice to wizard + persistent sub-line
    #         line.invoice_id = invoice.id
    #         nre_line.write({
    #             'invoice_id': invoice.id,
    #             'invoicing_status': 'invoiced',
    #             'invoiced_amount': billing_amount,
    #         })
    #         _logger.info(">>> Linked invoice %s to wizard line %s and persistent NRE line %s",
    #                      invoice.id, line.id, nre_line.id)
    #
    #     # --- Update remaining amount on sale.order.line ---
    #     total_invoiced = sum(nre_line.invoiced_amount for nre_line in self.env['sale.order.line.nre.sub']
    #                          .search([('sale_line_id', '=', sale_line.id)]))
    #     sale_line.nre_remaining_amount = sale_line.price_unit - total_invoiced
    #     _logger.info(">>> Updated sale_line %s remaining_amount = %s",
    #                  sale_line.id, sale_line.nre_remaining_amount)
    #
    #     # Return action → show first invoice
    #     if created_invoices:
    #         _logger.info(">>> Returning first invoice %s in form view", created_invoices[0].id)
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'account.move',
    #             'view_mode': 'form',
    #             'res_id': created_invoices[0].id,
    #             'target': 'current',
    #         }
    #     return True

    # def action_create_invoice(self):
    #     self.ensure_one()
    #     _logger.info(">>> Action Create Invoice triggered for sale_line_id %s", self.sale_line_id.id)
    #
    #     sale_line = self.sale_line_id
    #     order = sale_line.order_id
    #
    #     # Get only selected wizard lines
    #     active_ids = self.env.context.get("active_ids", [])
    #     lines_to_process = self.line_ids.filtered(lambda l: l.id in active_ids)
    #     if not lines_to_process:
    #         raise UserError(_("Please select at least one sub-line to create invoice."))
    #
    #     # --- Validation: billing % cannot exceed 100 ---
    #     total_percentage = sum(l.billing_percentage for l in self.line_ids)
    #     _logger.info(">>> Current total billing percentage: %s", total_percentage)
    #     if total_percentage > 100.0:
    #         raise UserError(_("Total Billing Percentage cannot exceed 100%%. Currently: %s") % total_percentage)
    #
    #     created_invoices = self.env['account.move']
    #
    #     for line in lines_to_process:
    #         _logger.info(">>> Processing wizard line %s with code %s", line.id, line.sub_line_code)
    #
    #         # --- Validation: already invoiced ---
    #         if line.invoice_id:
    #             raise UserError(_("Sub-line %s is already invoiced (Invoice %s).")
    #                             % (line.sub_line_code, line.invoice_id.name))
    #
    #         # Find persistent sub-line
    #         nre_line = self.env['sale.order.line.nre.sub'].search([
    #             ('sale_line_id', '=', sale_line.id),
    #             ('sub_line_code', '=', line.sub_line_code),
    #         ], limit=1)
    #
    #         if not nre_line:
    #             raise UserError(_("Persistent NRE sub-line not found for %s") % line.sub_line_code)
    #
    #         # Calculate billing amount
    #         billing_amount = (sale_line.price_unit * line.billing_percentage) / 100.0
    #         _logger.info(">>> Creating invoice for billing_amount %s", billing_amount)
    #
    #         # Create invoice
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
    #         # Link invoice to wizard + persistent sub-line
    #         line.invoice_id = invoice.id
    #         nre_line.write({
    #             'invoice_id': invoice.id,
    #             'invoicing_status': 'invoiced',
    #             'invoiced_amount': billing_amount,
    #         })
    #         _logger.info(">>> Linked invoice %s to wizard line %s and persistent NRE line %s",
    #                      invoice.id, line.id, nre_line.id)
    #
    #     # --- Update remaining amount on sale.order.line ---
    #     total_invoiced = sum(nre_line.invoiced_amount for nre_line in self.env['sale.order.line.nre.sub']
    #                          .search([('sale_line_id', '=', sale_line.id)]))
    #     sale_line.nre_remaining_amount = sale_line.price_unit - total_invoiced
    #     _logger.info(">>> Updated sale_line %s remaining_amount = %s",
    #                  sale_line.id, sale_line.nre_remaining_amount)
    #
    #     # Return action → show first invoice
    #     if created_invoices:
    #         _logger.info(">>> Returning first invoice %s in form view", created_invoices[0].id)
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'account.move',
    #             'view_mode': 'form',
    #             'res_id': created_invoices[0].id,
    #             'target': 'current',
    #         }
    #     return True

    def action_create_invoice(self):
        self.ensure_one()
        _logger.info(">>> Action Create Invoice triggered for sale_line_id %s", self.sale_line_id.id)

        sale_line = self.sale_line_id
        order = sale_line.order_id

        # Get only selected wizard lines
        lines_to_process = self.line_ids.filtered(lambda l: l.selected)
        if not lines_to_process:
            raise UserError(_("Please select at least one sub-line to create invoice."))

        # --- Validation: billing % cannot exceed 100 ---
        total_percentage = sum(l.billing_percentage for l in self.line_ids)
        _logger.info(">>> Current total billing percentage: %s", total_percentage)
        if total_percentage > 100.0:
            raise UserError(_("Total Billing Percentage cannot exceed 100%%. Currently: %s") % total_percentage)

        created_invoices = self.env['account.move']

        for line in lines_to_process:
            _logger.info(">>> Processing wizard line %s with code %s", line.id, line.sub_line_code)

            # --- Validation: already invoiced ---
            if line.invoice_id:
                raise UserError(_("Sub-line %s is already invoiced (Invoice %s).")
                                % (line.sub_line_code, line.invoice_id.name))

            # Find persistent NRE sub-line
            nre_line = self.env['sale.order.line.nre.sub'].search([
                ('sale_line_id', '=', sale_line.id),
                ('sub_line_code', '=', line.sub_line_code),
            ], limit=1)
            if not nre_line:
                raise UserError(_("Persistent NRE sub-line not found for %s") % line.sub_line_code)

            # Compute billing amount from wizard line field
            billing_amount = line.billing_amount
            _logger.info(">>> Creating invoice for billing_amount %s", billing_amount)

            # Create invoice
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': order.partner_id.id,
                'invoice_origin': order.name,
                'invoice_line_ids': [(0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.sub_line_description or sale_line.name,
                    'quantity': 1,
                    'price_unit': billing_amount,
                    'sale_line_ids': [(6, 0, [sale_line.id])],
                })],
            }
            invoice = self.env['account.move'].create(invoice_vals)
            created_invoices |= invoice

            # Link invoice to wizard line and persistent NRE sub-line
            line.invoice_id = invoice.id
            line.invoicing_status = 'invoiced'
            nre_line.write({
                'invoice_id': invoice.id,
                'invoicing_status': 'invoiced',
                'invoiced_amount': billing_amount,
            })
            _logger.info(">>> Linked invoice %s to wizard line %s and persistent NRE line %s",
                         invoice.id, line.id, nre_line.id)

        # --- Update remaining amount on main sale.order.line ---
        total_invoiced = sum(nre_line.invoiced_amount for nre_line in self.env['sale.order.line.nre.sub']
                             .search([('sale_line_id', '=', sale_line.id)]))
        sale_line.nre_remaining_amount = sale_line.price_unit - total_invoiced
        _logger.info(">>> Updated sale_line %s remaining_amount = %s",
                     sale_line.id, sale_line.nre_remaining_amount)

        # Return action → open first invoice form
        if created_invoices:
            _logger.info(">>> Returning first invoice %s in form view", created_invoices[0].id)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': created_invoices[0].id,
                'target': 'current',
            }

        return True

