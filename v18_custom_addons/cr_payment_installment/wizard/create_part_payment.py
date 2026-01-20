# -*- coding: utf-8 -*-
# Part of Creyox technologies.

from odoo import api, fields, models, _


class CrSubPartPaymentWizard(models.Model):
    _name = "cr.sub.part.payment.wizard"
    _description = "Sub Part Payment Wizard"
    _order = "index"

    pay_part_amount = fields.Float(string="Amount")

    def btn_pay_part_payment(self):
        if self.pay_part_amount > 0:
            active_move = self.env["account.move"].browse(self.env.context["active_id"])

            # Update installment lines for the invoice
            installment_lines = active_move.am_installment_line_ids.filtered(
                lambda x: x.index != 0
                and x.state == "draft"
                and x.description != "Part Payment"
            )
            total_installment_amount = sum(installment_lines.mapped("amount"))
            adjusted_amount_per_installment = (
                self.pay_part_amount / len(installment_lines)
                if installment_lines
                else 0.0
            )
            for line in installment_lines:
                line.update({"index": line.index + 1})
                line.amount -= adjusted_amount_per_installment
            if self.pay_part_amount == total_installment_amount:
                installment_lines.unlink()

            # Update installment lines for the sale order
            sale_order = (
                self.env["sale.order.line"]
                .search(
                    [
                        (
                            "id",
                            "in",
                            active_move.invoice_line_ids.mapped("sale_line_ids").ids,
                        )
                    ]
                )
                .order_id
            )
            sale_installment_lines = sale_order.installment_line_ids.filtered(
                lambda x: x.index != 0
            )
            total_sale_installment_amount = sum(sale_installment_lines.mapped("amount"))
            adjusted_amount_per_sale_installment = (
                self.pay_part_amount / len(sale_installment_lines)
                if sale_installment_lines
                else 0.0
            )
            for line in sale_installment_lines:
                line.update({"index": line.index + 1})
                line.amount -= adjusted_amount_per_sale_installment
            if self.pay_part_amount == total_sale_installment_amount:
                sale_installment_lines.unlink()

            # Create new installment line for the invoice
            line_vals = {
                "index": 1,
                "amount": self.pay_part_amount,
                "payment_date": fields.Date.today(),
                "description": "Part Payment",
                "invoice_id": active_move.id,
            }
            line_id = self.env["cr.invoice.installment.line"].create(line_vals)

            # Create new installment line for the sale order
            line_vals_sale = {
                "index": 1,
                "amount": self.pay_part_amount,
                "payment_date": fields.Date.today(),
                "description": "Part Payment",
                "sale_id": sale_order.id,
            }
            sale_line_id = self.env["cr.sale.installment.line"].create(line_vals_sale)
            line_id.so_installment_line_id = sale_line_id.id

            # Perform payment registration
            res = active_move.action_register_payment()

            # Update context
            res["context"].update(
                {
                    "default_amount": self.pay_part_amount,
                    "line_id": line_id.id,
                    "line_model": "cr.invoice.installment.line",
                    "dont_redirect_to_payments": True,
                }
            )
            return res
