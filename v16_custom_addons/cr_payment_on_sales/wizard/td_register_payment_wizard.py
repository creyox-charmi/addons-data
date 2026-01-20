# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_amount


class TdRegisterPaymentWizard(models.TransientModel):
    _name ="cr.register.payment.wizard"
    _description ="Register Payment"
    _check_company_auto = True

    sale_order_id = fields.Many2one("sale.order")
    # == Business fields ==
    payment_date = fields.Date(string="Payment Date", required=True,default=fields.Date.context_today)
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False,compute='_compute_amount')
    payment_type = fields.Selection([('outbound', 'Send Money'),('inbound', 'Receive Money'),], string='Payment Type', default='inbound')

    partner_id = fields.Many2one('res.partner',string="Customer/Vendor", store=True, copy=False, ondelete='restrict',related='sale_order_id.partner_id')
    company_id = fields.Many2one('res.company', store=True, copy=False,related='sale_order_id.company_id')
    currency_id = fields.Many2one(comodel_name='res.currency',string='Currency',related='sale_order_id.currency_id', store=True, readonly=False,help="The payment's currency.")
    company_currency_id = fields.Many2one('res.currency', string="Company Currency",related='company_id.currency_id')
    available_journal_ids = fields.Many2many(comodel_name='account.journal',compute='_compute_available_journal_ids')
    journal_id = fields.Many2one(comodel_name='account.journal',compute='_compute_journal_id', store=True, readonly=False, precompute=True,check_company=True,domain="[('id', 'in', available_journal_ids)]")

    available_partner_bank_ids = fields.Many2many(comodel_name='res.partner.bank',compute='_compute_available_partner_bank_ids',)
    partner_bank_id = fields.Many2one(comodel_name='res.partner.bank',string="Recipient Bank Account",readonly=False,store=True,compute='_compute_partner_bank_id',domain="[('id', 'in', available_partner_bank_ids)]")


    #  # == Payment methods fields ==
    available_payment_method_line_ids = fields.Many2many('account.payment.method.line', compute='_compute_payment_method_line_fields')
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method',readonly=False, store=True,compute='_compute_payment_method_line_id',domain="[('id', 'in', available_payment_method_line_ids)]",
        help="Manual: Pay or Get paid by any method outside of Odoo.\n"
        "Payment Providers: Each payment provider has its own Payment Method. Request a transaction on/to a card thanks to a payment token saved by the partner when buying or subscribing online.\n"
        "Check: Pay bills by check and print it from Odoo.\n"
        "Batch Deposit: Collect several customer checks at once generating and submitting a batch deposit to your bank. Module account_batch_payment is necessary.\n"
        "SEPA Credit Transfer: Pay in the SEPA zone by submitting a SEPA Credit Transfer file to your bank. Module account_sepa is necessary.\n"
        "SEPA Direct Debit: Get paid in the SEPA zone thanks to a mandate your partner will have granted to you. Module account_sepa is necessary.\n")

    # == Display purpose fields ==
    show_partner_bank_account = fields.Boolean(compute='_compute_show_require_partner_bank') # Used to know whether the field `partner_bank_id` should be displayed
    require_partner_bank_account = fields.Boolean(
        compute='_compute_show_require_partner_bank') # used to know whether the field `partner_bank_id` should be required
    country_code = fields.Char(related='company_id.account_fiscal_country_id.code', readonly=True)

    @api.depends('company_id', 'currency_id', 'payment_date')
    def _compute_amount(self):
        for wizard in self:
            if wizard.sale_order_id:
                wizard.amount = wizard.sale_order_id.cr_amount_residual
            else:
                wizard.amount = None    
    
    @api.depends('company_id')
    def _compute_available_journal_ids(self):
        for wizard in self:
            wizard.available_journal_ids = self.env['account.journal'].search([('type', 'in', ('bank', 'cash')),])

    @api.depends('available_journal_ids')
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = wizard.available_journal_ids[:1]

    @api.depends('journal_id')
    def _compute_available_partner_bank_ids(self):
        for wizard in self:
            wizard.available_partner_bank_ids = wizard.journal_id.bank_account_id
            
    @api.depends('journal_id', 'available_partner_bank_ids')
    def _compute_partner_bank_id(self):
        for wizard in self:
            available_partner_banks = wizard.available_partner_bank_ids._origin
            wizard.partner_bank_id = available_partner_banks[:1]
            
    @api.depends('payment_type', 'journal_id', 'currency_id')
    def _compute_payment_method_line_fields(self):
        for wizard in self:
            if wizard.journal_id:
                wizard.available_payment_method_line_ids = wizard.journal_id._get_available_payment_method_lines(wizard.payment_type)
            else:
                wizard.available_payment_method_line_ids = False

    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_id(self):
        for wizard in self:
            if wizard.journal_id:
                available_payment_method_lines = wizard.journal_id._get_available_payment_method_lines(wizard.payment_type)
            else:
                available_payment_method_lines = False

            # Select the first available one by default.
            if available_payment_method_lines:
                wizard.payment_method_line_id = available_payment_method_lines[0]._origin
            else:
                wizard.payment_method_line_id = False

    @api.depends('payment_method_line_id')
    def _compute_show_require_partner_bank(self):
        """ Computes if the destination bank account must be displayed in the payment form view. By default, it
        won't be displayed but some modules might change that, depending on the payment type."""
        for wizard in self:
            if wizard.journal_id.type == 'cash':
                wizard.show_partner_bank_account = False
            else:
                wizard.show_partner_bank_account = wizard.payment_method_line_id.code in self.env['account.payment']._get_method_codes_using_bank_account()
            wizard.require_partner_bank_account = wizard.payment_method_line_id.code in self.env['account.payment']._get_method_codes_needing_bank_account()

    def action_create_payments(self):
        for wizard in self:
            amount = wizard.currency_id._convert(wizard.amount, wizard.sale_order_id.currency_id, wizard.journal_id.company_id, wizard.payment_date)
            if not amount:
                raise ValidationError(_("Please enter Payment amount"))
            
            if amount > wizard.sale_order_id.cr_amount_residual:
                raise ValidationError(_(F"Amount paid ({format_amount(self.env,wizard.amount,wizard.currency_id)}, in {wizard.sale_order_id.currency_id.display_name} {format_amount(self.env,amount,wizard.sale_order_id.currency_id)}) is more than the amount due ({format_amount(self.env,wizard.sale_order_id.cr_amount_residual,wizard.sale_order_id.currency_id)})."))

            payment_values = {'payment_type': wizard.payment_type,
                            'partner_id':wizard.partner_id.id,
                            'partner_type': 'customer',
                            'journal_id': wizard.journal_id.id,
                            'company_id': wizard.company_id.id,
                            'currency_id': wizard.currency_id.id,
                            'date': wizard.payment_date,
                            'amount': wizard.amount,
                            'cr_sale_order_id': wizard.sale_order_id.id,
                            'ref': wizard.sale_order_id.name,
                            'partner_bank_id': wizard.partner_bank_id.id,
                            'payment_method_line_id': wizard.payment_method_line_id.id}
            payment = self.env['account.payment'].with_context(skip_invoice_sync=True).create(payment_values)
            payment.action_post()