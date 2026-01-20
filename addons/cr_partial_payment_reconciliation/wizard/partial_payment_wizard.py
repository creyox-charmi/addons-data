# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api
from odoo.exceptions import UserError


class PaymentWizard(models.TransientModel):
    _name = "partial.payment.wizard"
    _description = "Wizard for processing multiple payments"

    payment_name = fields.Char(string="Payment Name")
    partner_id = fields.Many2one("res.partner", string="Partner")
    partner_type = fields.Selection(
        [("customer", "Customer"), ("supplier", "Supplier")], string="Partner Type"
    )
    payment_type = fields.Selection(
        selection=[("inbound", "Customer Payment"), ("outbound", "Vendor Payment")]
    )
    account_move_line_id = fields.Many2one(
        "account.payment",
        string="Customer/Vendor Payment Line",
        domain="[('partner_id', '=', partner_id),('is_reconciled', '=', False)]",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
    )
    residual_amount = fields.Float(string="Residual Amount")
    remain_amount = fields.Float(string="Remain Amount")
    account_move_ids = fields.Many2many(
        "account.move",
        domain="[('partner_id', '=', partner_id), ('move_type', '=', 'out_invoice')]",
    )

    @api.onchange("partner_id", "partner_type")
    def _onchange_partner_id(self):
        """
        Updates the domain of 'account_move_ids' based on the selected `partner_id`
        and `partner_type`. Filters for posted invoices with unpaid or partial payments.

        Clears the domain if either `partner_id` or `partner_type` is not set.
        """
        if self.partner_id and self.partner_type:
            if self.partner_type == "customer":
                move_type = "out_invoice"
            elif self.partner_type == "supplier":
                move_type = "in_invoice"

            return {
                "domain": {
                    "account_move_ids": [
                        ("partner_id", "=", self.partner_id.id),
                        ("move_type", "=", move_type),
                        ("state", "=", "posted"),
                        ("payment_state", "in", ["not_paid", "partial"]),
                    ]
                }
            }
        else:
            return {"domain": {"account_move_ids": []}}

    @api.onchange("account_move_line_id")
    def _onchange_account_move_line_id(self):
        """
        Processes payments for the selected `account_move_ids`.

        - Based on the `move_type` of the associated account moves ('in_invoice' or 'out_invoice'),
        sets the `partner_type` (supplier/customer) and `payment_type` (outbound/inbound).
        - Checks if the remaining amount is sufficient for the payment.
        - Creates a new payment record and posts it, reconciling related payment lines if needed.
        - Updates the existing payment with the remaining balance after processing the current payments.

        Raises:
            UserError: If the entered amount exceeds the remaining amount.
        """
        self.residual_amount = self.account_move_line_id.amount
        self.remain_amount = self.account_move_line_id.amount

    def process_payment(self):
        account_move = self.account_move_ids
        existing_payment = self.env["account.payment"].search(
            [
                ("id", "=", self.account_move_line_id.id),
            ]
        )
        amount_to_pay = 0
        for move in account_move:
            if move.move_type == "in_invoice":
                self.partner_type = "supplier"
                self.payment_type = "outbound"
            elif move.move_type == "out_invoice":
                self.partner_type = "customer"
                self.payment_type = "inbound"
            if self.remain_amount < move.amount_to_pay:
                raise UserError(
                    "Entered amount cannot be more than the remaining amount."
                )

            payment = self.env["account.payment"].create(
                {
                    "partner_id": move.partner_id.id,
                    "company_id": self.env.user.company_id.id,
                    "date": self.account_move_line_id.date,
                    "amount": move.amount_to_pay,
                    "payment_type": self.payment_type,
                    "partner_type": self.partner_type,
                    "journal_id": self.account_move_line_id.journal_id.id,
                    "payment_method_line_id": self.account_move_line_id.journal_id.inbound_payment_method_line_ids.id,
                    "ref": self.payment_name,
                }
            )
            payment.action_post()
            if payment:
                line_ids = payment.mapped("move_id.line_ids").filtered(
                    lambda x: x.account_type
                    in ("asset_receivable", "liability_payable")
                    and not x.reconciled
                )
                if line_ids:
                    reconcile_line = move.line_ids.filtered(
                        lambda x: x.account_type
                        in ("asset_receivable", "liability_payable")
                        and not x.reconciled
                    )
                    if reconcile_line:
                        line_ids += reconcile_line
                        line_ids.reconcile()
                amount_to_pay += move.amount_to_pay
        existing_payment.amount = self.remain_amount - amount_to_pay
