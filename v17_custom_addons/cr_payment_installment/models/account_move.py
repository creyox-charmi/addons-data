# -*- coding: utf-8 -*-
# Part of Creyox technologies.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = "account.move"

    am_installment_line_ids = fields.One2many(
        "cr.invoice.installment.line", "invoice_id", "Installments"
    )
    am_month_tenure = fields.Integer(
        string="Tenure (months)",
    )
    am_installment_amount = fields.Float(
        string="Installment Amount",
    )
    am_compute_installment = fields.Char(string="Compute")
    is_am_sale_installment = fields.Boolean(string="Sale Installment")
    am_part_payment = fields.Char(string="Part Payment")
    am_down_payment_amount = fields.Float(
        string="Down Payment",
    )
    am_second_payment_date = fields.Date()
    am_payable_amount = fields.Float(
        string="Payable Amount",
    )
    am_tenure_amount = fields.Float(
        compute="_compute_tenure_amount", string="Tenure Amount"
    )

    def btn_open_partial_payment(self):
        ctx = {
            "default_move_id": self.id,
        }
        return {
            "name": "Partial Payment",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "cr.sub.part.payment.wizard",
            "view_id": self.env.ref(
                "cr_payment_installment.cr_sub_part_payment_confirm_form_view", "False"
            ).id,
            "context": ctx,
            "target": "new",
        }

    @api.onchange("am_installment_amount")
    def _onchange_installment_tenure_amount(self):
        if self.am_installment_amount:
            self.am_month_tenure = round(
                self.amount_residual / self.am_installment_amount
            )

    @api.onchange("am_month_tenure")
    def _onchange_month_tenure(self):
        if self.am_month_tenure:
            self.am_installment_amount = round(
                self.amount_residual / self.am_month_tenure
            )

    def onchange(self, values, field_name, field_onchange):
        return super(
            AccountMove, self.with_context(recursive_onchanges=False)
        ).onchange(values, field_name, field_onchange)

    @api.depends("amount_total")
    def _compute_tenure_amount(self):
        for record in self:
            record.am_tenure_amount = record.amount_total

    def compute_installment(self):
        for order in self:
            installment_lines = []

            # Retrieve necessary data
            installment_amount = order.am_installment_amount
            amount_total = order.amount_residual
            month_tenure = order.am_month_tenure

            # Check if installment amount is set and there is an outstanding amount
            if installment_amount and amount_total:
                payment_date = order.am_installment_line_ids.filtered(
                    lambda x: x.state == "draft"
                )[0].payment_date
                order.am_installment_line_ids.filtered(
                    lambda x: x.state == "draft"
                ).unlink()

                # Assuming order.invoice_line_ids is a One2many field
                sale_order_lines = self.env["sale.order.line"].search(
                    [("id", "in", order.invoice_line_ids.mapped("sale_line_ids").ids)]
                )
                sale_order_line_id = (
                    self.env["sale.order.line"]
                    .search(
                        [
                            (
                                "id",
                                "in",
                                order.invoice_line_ids.mapped("sale_line_ids").ids,
                            )
                        ]
                    )
                    .order_id
                )
                sale_order_line_id.installment_line_ids.filtered(
                    lambda x: x.state == "draft"
                ).unlink()

                index = 1
                while month_tenure > 0:
                    if amount_total < 0.0:
                        raise UserError(
                            _(
                                "Installment Amount Or Number Of Installment Mismatch Error."
                            )
                        )

                    # Calculate the installment amount for the current month
                    installment_amount = (
                        min(installment_amount, amount_total)
                        if month_tenure == 1
                        else installment_amount
                    )

                    # Create installment line
                    installment_line = {
                        "index": index,
                        "amount": installment_amount,
                        "payment_date": payment_date,
                        "description": f"{index} installment",
                        "sale_id": sale_order_lines
                        and sale_order_lines.order_id.id
                        or False,
                    }
                    installment_lines.append((0, 0, installment_line))
                    # Update variables for the next iteration
                    amount_total -= installment_amount
                    index += 1
                    month_tenure -= 1
                    payment_date += relativedelta(months=1)

                # Update the installment lines on the current order
                if installment_lines:
                    order.am_installment_line_ids = installment_lines
