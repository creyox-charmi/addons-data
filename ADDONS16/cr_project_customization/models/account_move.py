# -*- coding: utf-8 -*-
# Part of Creyox technologies.

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    task_id = fields.Many2one("project.task", string="Task Ref")

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        
        if self.env.context.get('active_id'):
            account_id = self.env["account.move"].browse(self.env.context.get('active_id'))
            ##### BIll for Developer
            if account_id and account_id.task_id and account_id.payment_state == 'paid' and account_id.move_type == "in_invoice":
                account_id.task_id.dev_payment_status = "paid"
            if account_id and account_id.task_id and account_id.payment_state == 'partial' and account_id.move_type == "in_invoice":
                account_id.task_id.dev_payment_status = "partial"
            ##### Invoice for Task 
            if account_id and account_id.task_id and account_id.payment_state == 'paid' and account_id.move_type == "out_invoice":
                project_task_type_id = self.env["project.task.type"].search([("is_paid", "=", True)])
                account_id.task_id.task_payment_status = "paid"
                if project_task_type_id:
                     account_id.task_id.stage_id = project_task_type_id.id
            if account_id and account_id.task_id and account_id.payment_state == 'partial' and account_id.move_type == "out_invoice":
                account_id.task_id.task_payment_status = "partial"

