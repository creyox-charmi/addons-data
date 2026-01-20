# -*- coding: utf-8 -*-
# Part of Creyox technologies.
from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, fields):
        result = super(AccountPayment, self).default_get(fields)
        context = self.env.context
        if context.get("default_amount"):
            result.update({"amount": context["default_amount"]})
        return result

    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date):
        result = super(AccountPayment, self)._compute_payment_amount(
            invoices, currency, journal, date
        )
        if self.env.context.get("default_amount"):
            return self.env.context["default_amount"]
        return result

    def action_post(self):
        result = super(AccountPayment, self).action_post()

        line_model = self.env.context.get("line_model")
        line_id = self.env.context.get("line_id")

        if line_model and line_id:
            payment_line = self.env[line_model].browse(line_id)
            payment_line.state = "paid"
            payment_line.so_installment_line_id.state = "paid"

            move_id = self.env.context.get("active_id")
            if move_id:
                installment_lines = (
                    self.env["account.move"]
                    .browse(move_id)
                    .am_installment_line_ids.filtered(lambda x: x.index != 0)
                )
                for installment_line in installment_lines:
                    installment_line.update({"index": installment_line.index})

        return result
