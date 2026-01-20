# -*- coding: utf-8 -*-
# Part of Creyox technologies.

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class CrInvoiceInstallmentLine(models.Model):
    _name = "cr.invoice.installment.line"
    _description = "Invoice Installment Line"
    _order = "payment_date"
    _rec_name = "description"

    amount = fields.Float(string="Amount")
    index = fields.Integer(string="No")
    invoice_id = fields.Many2one("account.move", "Invoice", ondelete="cascade")
    sale_id = fields.Many2one("sale.order", "Sale Order", ondelete="cascade")
    payment_date = fields.Date(string="Payment Date")
    description = fields.Char(string="Description")
    is_paid = fields.Boolean(string="Paid?")
    so_installment_line_id = fields.Many2one(
        "cr.sale.installment.line", "Sale Installment Line"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("paid", "Paid")], default="draft", string="Status"
    )

    def make_payment(self):
        active_move = self.env["account.move"].browse(self.invoice_id.id)
        payment_context = {
            "default_amount": self.amount,
            "line_id": self.id,
            "line_model": "cr.invoice.installment.line",
            "dont_redirect_to_payments": True,
        }

        res = active_move.action_register_payment()
        res["context"].update(payment_context)
        return res

    @api.model
    def payment_installment_reminder(self):
        tommorow = fields.Datetime.today() + relativedelta(days=1)
        day_after_tommorow = fields.Datetime.today() + relativedelta(days=2)
        records = self.search(
            [
                ("invoice_id.state", "=", "posted"),
                "|",
                ("payment_date", "=", tommorow),
                ("payment_date", "=", day_after_tommorow),
            ]
        )
        for rec in records:
            template = self.env.ref(
                "cr_payment_installment.mail_template_installment_reminder"
            )
            template.send_mail(rec.id, force_send=False)
