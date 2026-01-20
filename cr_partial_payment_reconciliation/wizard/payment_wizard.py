# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api
from odoo.exceptions import UserError


class PaymentWizard(models.TransientModel):
    _name = "payment.wizard"
    _description = "Wizard for processing single payments"

    amount_total = fields.Float(string="Amount Total", compute="_compute_amount_total")
    amount_due = fields.Float(string="Amount Due")
    account_move_id = fields.Many2one("account.move", string="Account Move")
    currency_id = fields.Many2one("res.currency", string="Currency")
    amount_to_pay = fields.Float(string="Amount to Pay")
    partner_id = fields.Many2one("res.partner", string="Partner")
    account_move_line_id = fields.Many2one(
        "account.payment",
        string="Account Move Line",
        domain="[('partner_id', '=', partner_id),('is_reconciled', '=', False)]",
    )
    payment = fields.Char(string="Payment")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company.id
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        string="Company Currency",
        default=lambda self: self.env.company.currency_id.id,
    )
    remaining_amount_for_payment = fields.Float(string="Remaining Amount for Payment")
    remaining_amount_for_invoice = fields.Float(string="Remaining Amount for Invoice")
    partner_type = fields.Selection(
        [("customer", "Customer"), ("supplier", "supplier")], string="Partner Type"
    )

    @api.depends("account_move_line_id")
    def _compute_amount_total(self):
        """
        Computes the total amount based on the account move line's amount.
        """
        for wizard in self:
            if wizard.account_move_line_id:
                wizard.amount_total = wizard.account_move_line_id.amount
                wizard.remaining_amount_for_payment = wizard.account_move_line_id.amount
            else:
                wizard.amount_total = 0.00
                wizard.remaining_amount_for_payment = 0.00

    @api.model
    def default_get(self, fields):
        """
        Sets default values for the PaymentWizard based on the related `account.move`.
        Defaults include `currency_id`, `amount_due`, `remaining_amount_for_invoice`, and `payment`.
        """
        res = super(PaymentWizard, self).default_get(fields)
        rec = self.env["account.move"].browse(res["account_move_id"])
        res["currency_id"] = rec.currency_id.id
        res["amount_due"] = rec.amount_residual
        res["remaining_amount_for_invoice"] = rec.amount_residual
        res["payment"] = rec.payment_reference
        res["partner_id"] = rec.partner_id.id

        return res

    @api.onchange("amount_to_pay")
    def _onchange_amount_to_pay(self):
        """Update remaining amounts based on the amount to pay."""
        if self.amount_to_pay:
            if self.amount_to_pay > self.remaining_amount_for_invoice:
                raise UserError(
                    f"The amount to pay ({self.amount_to_pay}) cannot exceed the remaining invoice amount ({self.remaining_amount_for_invoice})."
                )

            self.remaining_amount_for_invoice = (
                self.remaining_amount_for_invoice - self.amount_to_pay
            )
            self.remaining_amount_for_payment = (
                self.remaining_amount_for_payment - self.amount_to_pay
            )

    def process_payment(self):
        """
        Processes a payment for the associated `account_move_id`, creates a payment record,
        and reconciles related lines if necessary.

        - Sets `partner_type` and `payment_type` based on `move_type` ('in_invoice' or 'out_invoice').
        - Creates and posts a payment, updates the existing payment with the remaining amount.
        - Reconciles related lines if applicable.
        """
        account_move = self.account_move_id
        existing_payment = self.env["account.payment"].search(
            [
                ("id", "=", self.account_move_line_id.id),
            ]
        )
        if account_move.move_type == "in_invoice":
            self.partner_type = "supplier"
            payment_type = "outbound"
        elif account_move.move_type == "out_invoice":
            self.partner_type = "customer"
            payment_type = "inbound"

        payment = self.env["account.payment"].create(
            {
                "partner_id": account_move.partner_id.id,
                "company_id": self.env.user.company_id.id,
                "date": self.account_move_line_id.date,
                "amount": self.amount_to_pay,
                "payment_type": payment_type,
                "partner_type": self.partner_type,
                "journal_id": self.account_move_line_id.journal_id.id,
                "payment_method_line_id": self.account_move_line_id.journal_id.inbound_payment_method_line_ids.id,
                "ref": account_move.name,
            }
        )
        payment.action_post()

        if payment:
            line_ids = payment.mapped("move_id.line_ids").filtered(
                lambda x: x.account_type in ("asset_receivable", "liability_payable")
                and not x.reconciled
            )
            if line_ids:
                reconcile_line = account_move.line_ids.filtered(
                    lambda x: x.account_type
                    in ("asset_receivable", "liability_payable")
                    and not x.reconciled
                )
                if reconcile_line:
                    line_ids += reconcile_line
                    line_ids.reconcile()
        existing_payment.amount = self.remaining_amount_for_payment - self.amount_to_pay
