# -*- coding: utf-8 -*-
# Part of Creyox technologies.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    installment_line_ids = fields.One2many(
        "cr.sale.installment.line", "sale_id", string="Installments"
    )
    down_payment_amount = fields.Float(
        string="Down Payment",
    )
    installment_payment_date = fields.Date(
        string="Installment Payment Date",
        readonly=True,

    )
    installment_amount = fields.Float(
        string="Installment Amount",
        readonly=True,
    )
    total_payable_amount = fields.Float(
        string="Payable Amount",
    )
    months_tenure = fields.Integer(
        string="Tenure (months)",
    )
    tenure_amount = fields.Float(
        compute="_compute_tenure_amount", string="Tenure Amount"
    )

    @api.depends("amount_total")
    def _compute_tenure_amount(self):
        for record in self:
            record.tenure_amount = record.amount_total

    @api.onchange("installment_amount")
    def _onchange_installment_amt_tenure(self):
        if self.installment_amount:
            self.with_context(
                {"installment_amount": self.installment_amount}
            ).months_tenure = round(self.total_payable_amount / self.installment_amount)

    @api.onchange("months_tenure")
    def _onchange_tenure(self):
        if self.months_tenure:
            self.installment_amount = round(
                self.total_payable_amount / self.months_tenure
            )

    def onchange(self, values, field_name, field_onchange):
        return super(SaleOrder, self.with_context(recursive_onchanges=False)).onchange(
            values, field_name, field_onchange
        )

    @api.onchange("down_payment_amount", "order_line")
    def _onchange_down_payment_amt(self):
        if self.amount_total:
            self.total_payable_amount = self.amount_total - self.down_payment_amount

    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ["cancel", "sent"])
        orders.installment_line_ids.unlink()

        draft_values = {
            "down_payment_amount": 0.0,
            "installment_amount": 0.0,
            "installment_payment_date": False,
            "total_payable_amount": 0.0,
            "months_tenure": 1,
        }

        orders.write(draft_values)
        result = super(SaleOrder, self).action_draft()
        return result

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()

        for order in self:
            amount_total = order.total_payable_amount
            months_tenure = order.months_tenure
            installment_amount = order.installment_amount
            payment_date = order.installment_payment_date or fields.Date.today()

            if order.down_payment_amount:
                order._create_installment(
                    0, order.down_payment_amount, "Down Payment", payment_date
                )

            if amount_total < 0.0:
                raise UserError(
                    _("Installment Amount Or Number Of Installment Mismatch Error.")
                )

            for index in range(1, months_tenure + 1):
                amount = (
                    min(amount_total, installment_amount)
                    if index == months_tenure
                    else installment_amount
                )
                description = f"{index} installment"

                order._create_installment(index, amount, description, payment_date)
                payment_date = payment_date + relativedelta(months=1)

                amount_total -= installment_amount

            """
             # Payment terms will create when terms is not selected in SO. 
            """
            if order.installment_line_ids and not order.payment_term_id:
                installment_lines = order.installment_line_ids.filtered(
                    lambda x: x.index != 0
                )
                count = 30

                payment_term_vals = {
                    "name": "Payment Installment %s" % (order.partner_id.name),
                    "sale_order_id": order.id,
                }

                payment_term = self.env["account.payment.term"].create(
                    payment_term_vals
                )

                inst_line_data = []

                for index, inst_line in enumerate(installment_lines):
                    line_vals = {
                        "value": "fixed",
                        "value_amount": order.installment_amount,
                        "days": count,
                        "option": "day_after_invoice_date",
                        "day_of_the_month": 0,
                        "sequence": index,
                    }
                    inst_line_data.append((0, 0, line_vals))
                    count += 30

                payment_term.line_ids.update(
                    {
                        "sequence": len(installment_lines) + 1,
                        "value_amount": installment_lines[-1:].amount,
                        "days": count + 30,
                    }
                )

                payment_term.line_ids = inst_line_data
                order.payment_term_id = payment_term.id

        return result

    def _create_installment(self, index, amount, description, payment_date):
        self.ensure_one()
        installment_vals = {
            "index": index,
            "amount": amount,
            "payment_date": payment_date,
            "description": description,
        }
        self.write({"installment_line_ids": [(0, 0, installment_vals)]})

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()

        installment_line_ids = [
            (
                0,
                0,
                {
                    "index": line.index,
                    "amount": line.amount,
                    "payment_date": line.payment_date,
                    "description": line.description,
                    "so_installment_line_id": line.id,
                },
            )
            for order in self
            for line in order.installment_line_ids
        ]

        vals = {
            "am_month_tenure": self.months_tenure,
            "am_installment_amount": self.installment_amount,
            "am_down_payment_amount": self.down_payment_amount,
            "am_payable_amount": self.total_payable_amount,
            "am_installment_line_ids": installment_line_ids,
        }

        res.update(vals)

        return res

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if "installment_line_ids" in vals:
            for order in self:
                total_installment_amount = sum(
                    order.installment_line_ids.mapped("amount")
                )

                if total_installment_amount > order.amount_total:
                    raise UserError(
                        _("Installment Amount Or Number Of Installment Mismatch Error.")
                    )

        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    installments = fields.Integer(string="#Installments")
