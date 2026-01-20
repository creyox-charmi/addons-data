from odoo import models, api, exceptions
from odoo.exceptions import AccessError, UserError
from odoo import Command, models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # payment_state = fields.Selection(
    #     [
    #         ('not_paid','Note Paid'),
    #         ('paid','Paid'),
    #         ('pending','Pending')
    #     ],
    #     string = 'Payment Status',
    #     readonly = True,
    # )

    @api.model
    def create(self, values):
        """
        Overrides the create method to restrict purchase order creation
        for users in the 'Security' or 'Cashier' groups.
        """
        if self.env.user.has_group('cr_scrap_management.group_security') or \
           self.env.user.has_group('cr_scrap_management.group_cashier'):
            raise AccessError("You do not have permission to create Purchase Orders.")

        # Proceed with the creation if the user is allowed to create
        return super(PurchaseOrder, self).create(values)

    def action_print_receipt(self):
        """
        Prints the receipt for confirmed purchase orders.
        Raises an error if the order is not confirmed.
        """
        if self.state != 'purchase':
            raise exceptions.UserError("You can only print the receipt for confirmed orders.")
        return self.env.ref('cr_scrap_management.action_report_purchase_order_receipt').report_action(self)

    def action_create_bill(self):
        """
        Creates an invoice for the purchase order and triggers the payment wizard if the invoice is posted.
        """
        invoice = self.action_create_invoice()
        data_id = invoice['res_id']
        move = self.env['account.move'].search(
            [
                ('id','=',data_id)
            ]
        )
        if move:
            move.invoice_date = fields.Date.context_today(self)
            post_action = move.action_post()

        if move.state == 'posted':
            # Trigger the payment wizard and prepare the context manually
            payment_register_model = self.env['account.payment.register']

            # Get the journal_id from the move
            journal = self.env['account.journal'].search([('type','=','cash')],limit=1)
            payment_type = 'outbound'


            context = {
                'active_model': 'account.move.line',
                'active_ids': move.line_ids.ids,
                'journal_id': journal.id,
                'payment_date': fields.Date.today(),
                'type':journal.type,
                'amount': move.amount_total,
                'communication': move.name,
                'payment_type': payment_type,
            }

            # Create the wizard record and pass the updated context
            wizard = payment_register_model.with_context(context).create({
                'journal_id': journal.id,
                'payment_date': fields.Date.today(),
                'amount': move.amount_total,
                'communication': move.name,
                'payment_method_line_id': journal.outbound_payment_method_line_ids.id,
            })

            if wizard:
                wizard.action_create_payments()
            return self.action_view_invoice_payent(move)

    def action_view_invoice_payent(self, invoices=False):
        """
        Displays the invoice payment view based on the given invoices.
        If multiple invoices, it shows a list; for a single invoice, it shows the form view.
        """
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result
