# -*- coding: utf-8 -*-
# Part of Creyox technologies.

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime



class Task(models.Model):
    _inherit = "project.task"

    developer_amount = fields.Float(string="Developer Amount")
    dev_currency_id = fields.Many2one("res.currency", string="Client Currency")
    dev_payment_status = fields.Selection([("paid","Paid"), ("partial", "Partial"),("unpaid", "Unpaid")], default='unpaid',string="Developer Payment Status",)
    total_amount = fields.Float(string="Total Amount")
    currency_id = fields.Many2one("res.currency", string="Currency")
    approved_hours = fields.Float(string="Approved Hours")
    task_payment_status = fields.Selection([("paid","Paid"), ("partial", "Partial"),("unpaid", "Unpaid")], default='unpaid',string="Task Payment Status",)

    invoice_ids = fields.Many2many('account.move', copy=False)
    invoice_count = fields.Integer(compute='compute_get_invoices', copy=False)

    bill_ids = fields.Many2many('account.move', 'developer_bill', copy=False)
    bill_count = fields.Integer(compute='compute_get_bills', copy=False)



    @api.depends('invoice_ids')
    def compute_get_invoices(self):
        self.invoice_count = 0.0
        for record in self:
            count = 0
            invoices = []
            for inv in record.invoice_ids:
                if inv.state != 'cancel':
                    count += 1
                    invoices.append(inv.id)
            record.invoice_count = count
            return invoices

    def action_customer_invoice_view(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', 'in', self.compute_get_invoices())]
        action['context'] = {'create': False}
        return action

    @api.onchange('approved_hours')
    def _onchange_total_amount(self):
        if self.approved_hours and self.project_id.client_hourly_rate:

            self.env.context = dict(self.env.context)
            self.env.context.update({
            'is_call': True,
            })
            is_call_total_amount = self.env.context.get("is_call_total_amount")
            if not is_call_total_amount:
                self.total_amount = (self.approved_hours*self.project_id.client_hourly_rate)
                self.env.context.update({
            'is_call_total_amount': False,
            })

                

    @api.onchange('total_amount')
    def _onchange_approved_hours(self):
        if self.total_amount and self.project_id.client_hourly_rate:
            self.env.context = dict(self.env.context)
            self.env.context.update({
            'is_call_total_amount': True,
            })
            is_call = self.env.context.get("is_call")
            if not is_call:
                self.approved_hours = (self.total_amount/self.project_id.client_hourly_rate)
                self.env.context.update({
            'is_call': False,
            })

    @api.depends('bill_ids')
    def compute_get_bills(self):
        self.bill_count = 0.0
        for record in self:
            count = 0
            bills = []
            for inv in record.bill_ids:
                if inv.state != 'cancel':
                    count += 1
                    bills.append(inv.id)
            record.bill_count = count
            return bills

    def action_customer_bill_view(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        action['domain'] = [('id', 'in', self.compute_get_bills())]
        action['context'] = {'create': False}
        return action


    def button_task_bill(self):
        task_bill = {
            "partner_id": self.user_ids.partner_id.id,
            "company_id": self.company_id.id,
            "invoice_date": datetime.today(),
            "move_type": "in_invoice",
            "task_id": self.id,
            "ref": self.name,
            "currency_id": self.dev_currency_id.id
        }
        task_bill_id = self.env["account.move"].create(task_bill)
        bill_lines = [] 
        bill_lines.append((0,0,{
                            'name': self.name,
                            'quantity': 1,
                            'price_unit': self.developer_amount,
                            }))                          
        if task_bill_id:
            task_bill_id.invoice_line_ids = bill_lines
            active_ids = self._context.get('active_id')
            self.bill_ids = self.bill_ids.ids + [task_bill_id.id]

            return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_id': self.env.ref('account.view_move_form').id,
                    'res_model': 'account.move',
                    'res_id': task_bill_id.id,
                    'target': 'current',
                    }

    @api.model
    def default_get(self, default_fields):
        currency_id = self.env["res.currency"].search([("name", "=", 'INR')],limit=1)
        if self.project_id and self.project_id.client_currency_id:
            self.currency_id =  self.project_id.client_currency_id.id
        if currency_id:
           self.dev_currency_id = currency_id.id
        return super(Task, self).default_get(default_fields)

