##############################################################################

from odoo import fields, models,api,_

class PaymentTranscation(models.Model):
    _inherit = 'payment.transaction'

    # ====Link Tracker=====#
    utm_source_id = fields.Many2one('utm.source', ondelete='cascade', string="Source")
    utm_campaign_id = fields.Many2one('utm.campaign', string='UTM Campaign')
    utm_medium_id = fields.Many2one('utm.medium', string="Medium")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # ====Link Tracker=====#
    utm_source_id = fields.Many2one(related='payment_transaction_id.utm_source_id')
    utm_campaign_id = fields.Many2one(related='payment_transaction_id.utm_campaign_id')
    utm_medium_id = fields.Many2one(related='payment_transaction_id.utm_medium_id')


    def create_receipt(self, payments):
        # Function used to create receipt
        payments._compute_stat_buttons_from_reconciliation()
        res = self.get_reconcile_ids(payments)
        invoice_id = self.env['account.move'].browse(
            res[0].get('invoice_ids', [])) if res else False
        name = ''
        if not self.company_id._fields.get('is_tranzila_document',
                                           False) or not self.company_id._fields.get(
                'is_greeninvoice_document',
                False) or not self.company_id._fields.get('is_i4u_document',
                                                          False):
            name = ''

        rec_vals = {
            'name': name,
            'receipt_user_id': False,
            'partner_id': payments[0].partner_id.id,
            'company_id': payments[0].company_id.id,
            'date': payments[0].date,
            'subject': "תשלום מקוון" if payments[
                0].payment_transaction_id else "",
            'is_donation': payments[0].is_donation,
            'utm_source_id': payments[0].utm_source_id and payments[0].utm_source_id.id or False,
            'utm_campaign_id': payments[0].utm_campaign_id and payments[0].utm_campaign_id.id or False,
            'utm_medium_id': payments[0].utm_medium_id and payments[0].utm_medium_id.id or False,
            'bu_community_id': payments[0].utm_campaign_id.bu_community_id.id if payments[0].utm_campaign_id and
                                                                                 payments[
                                                                                     0].utm_campaign_id.bu_community_id else False,
            'receipt_line_ids': [
                (0, 0, {'journal_id': payment.journal_id.id,
                        'type': 'invoice' if invoice_id else 'generic',
                        'invoice_id': invoice_id.id if invoice_id else None,
                        'invoice_amount': payment.reconciled_invoice_ids[
                            0].amount_residual if payment.reconciled_invoice_ids else 0.0,
                        'amount': payment.amount,
                        'means_of_payment': '3'}) for payment
                in payments]
        }
        receipt_id = self.env['lyg.account.receipt'].with_context(
            wizard_payment=True).create(rec_vals)
        if receipt_id.is_donation:
            receipt_id.name = self.env['ir.sequence'].next_by_code(
                'lyg.donation.receipt') or _('New')
        else:
            receipt_id.name = self.env['ir.sequence'].next_by_code(
                'lyg.account.receipt') or _('New')
        payments.write({'receipt_id': receipt_id.id, 'means_of_payment': '3'})
        receipt_id.write({'state': 'post'})
        return receipt_id


