# -*- coding: utf-8 -*-
# Email: sales@creyox.com

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime



class TaskInvoice(models.TransientModel):
    _name = 'task.invoice'
    _description = 'Task Invoice'

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    count = fields.Integer(default=_count)
    company_id = fields.Many2one('res.company')

    def create_task_invoices(self):
        active_ids = self._context.get('active_ids')
        invoice_line = []
        invoice = self.env['account.move']
        invoice_id = self.env['account.move']
        if active_ids:
            if len(active_ids) == 1:
                for record in active_ids:
                    task_ids = self.env['project.task'].browse(record)
                    print("task_ids=============================================",task_ids)
                    for task_id in task_ids:
                        task_data = {
                            #'product_id': task_id.product_id.id,
                            'name': task_id.name,
                            'quantity': task_id.approved_hours,
                            'price_unit': task_id.project_id.client_hourly_rate,
                            #'tax_ids': task_id.product_id.taxes_id.ids,
                        }
                        invoice_line.append((0, 0, task_data))
                        # if order.state not in ['confirmed', 'progress', 'done']:
                        #     raise UserError(
                        #         _("%s Order is in %s state.\nOrder state must be in Confirmed, In Progress or Done state." % (
                        #         order.name, order.state)))

                    if self.company_id.account_fiscal_country_id.code == 'IN' and invoice_line:
                        invoice_id = invoice.create({
                            'partner_id': task_ids.partner_id.id,
                            "invoice_date": datetime.today(),
                            'move_type': 'out_invoice',
                            'invoice_line_ids': invoice_line,
                        })
                        if not task_ids.partner_id.l10n_in_gst_treatment:
                            gst_treatment = 'consumer'
                        else:
                            gst_treatment = self.task_id.l10n_in_gst_treatment
                        invoice_id.l10n_in_gst_treatment = gst_treatment
                    elif invoice_line:
                        invoice_id = invoice.create({
                            'partner_id': task_ids.partner_id.id,
                            'move_type': 'out_invoice',
                            'invoice_line_ids': invoice_line,
                        })
                    if invoice_id:

                        invoice_id.task_id = task_ids.id
                        invoice_id.ref= task_ids.name
                        invoice_id.currency_id = task_ids.currency_id.id
                        
                        active_ids = self._context.get('active_ids')
                        for record in active_ids:
                            task_ids = self.env['project.task'].browse(record)
                            for order in task_ids:
                                order.invoice_ids = order.invoice_ids.ids + [invoice_id.id]
                    if self.env.context.get('open_mo_invoices'):
                        return {
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'view_id': self.env.ref('account.view_move_form').id,
                            'res_model': 'account.move',
                            'res_id': invoice_id.id,
                            'target': 'current',
                        }
