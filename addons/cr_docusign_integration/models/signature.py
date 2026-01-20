# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients
import os
import shutil

class Signature(models.Model):
    _name = 'cr.signature'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Signature Management'
    _rec_name='cr_seq_name'

    cr_seq_name = fields.Char(string='Sequence', readonly=True)
    cr_status = fields.Selection(
        [('new', 'New'),
         ('open', 'Open'),
         ('sent', 'Sent'),
         ('completed', 'Completed')],
        default='new',
    )
    cr_is_doc_sent=fields.Boolean()
    cr_docusign_envelope_id = fields.Char(string='DocuSign Envelope ID', readonly=True, copy=False)
    cr_responsible = fields.Many2one('res.users', string='Responsible')
    cr_model_reference = fields.Char(string='Model Reference')
    cr_attachment = fields.Binary(string='Attachment (PDF Only)', attachment=True, required=True)
    cr_contact = fields.Char(string='Contact')
    cr_sale_order_name = fields.Char(string='Sale Order')
    cr_purchase_order_name = fields.Char(string='Purchase Order')
    cr_invoice_name = fields.Char(string='Invoice ')
    cr_docusign_account = fields.Char(string='DocuSign Account')
    cr_docs_policy = fields.Selection([
        ('simultaneously', 'Simultaneously'),
        ('hierarchy', 'In Hierarchy'),
    ], string='Document Sending Policy', default='simultaneously')
    cr_recipients = fields.One2many('cr.recipients', 'cr_sign', string='Recipients')
    cr_contact_id = fields.Many2one('res.partner',  string='partner')
    cr_sale_order_id = fields.Many2one('sale.order',  string='sale')
    cr_purchase_order_id = fields.Many2one('purchase.order',  string='purchase')
    cr_invoice_id = fields.Many2one('account.move',  string='invoice')
    cr_last_signed=fields.Char()
    invisible_contact = fields.Boolean(compute='_compute_visibility',store=True)
    invisible_sale_order = fields.Boolean(compute='_compute_visibility',store=True)
    invisible_purchase_order = fields.Boolean(compute='_compute_visibility',store=True)
    invisible_invoice = fields.Boolean(compute='_compute_visibility',store=True)

    @api.depends('cr_contact', 'cr_sale_order_name', 'cr_purchase_order_name', 'cr_invoice_name')
    def _compute_visibility(self):
        """This method ensures that only one field is visible at a time."""

        for record in self:
            record.invisible_contact = bool(
                record.cr_sale_order_name or record.cr_purchase_order_name or record.cr_invoice_name)
            record.invisible_sale_order = bool(
                record.cr_contact or record.cr_purchase_order_name or record.cr_invoice_name)
            record.invisible_purchase_order = bool(
                record.cr_contact or record.cr_sale_order_name or record.cr_invoice_name)
            record.invisible_invoice = bool(
                record.cr_contact or record.cr_sale_order_name or record.cr_purchase_order_name)

    @api.model
    def create(self, vals):
        """ Override the create method to ensure a unique sequence name is generated """
        if 'cr_seq_name' not in vals or not vals['cr_seq_name']:
            vals['cr_seq_name'] = self.env['ir.sequence'].next_by_code('cr.signature')
        return super(Signature, self).create(vals)

    def action_send_doc(self):
        """ Sends a document for signature via DocuSign and notifies the responsible person."""

        self.ensure_one()
        if not self.cr_docs_policy:
            raise UserError(_("Please assign a Doc policy"))

        if not self.cr_responsible:
            raise UserError(_("Please assign a responsible person."))
        else:
            user = self.cr_responsible.partner_id
            try:
                mail_values = {
                    'subject': _('New Assignment Notification'),
                    'body_html': f'''
                            <p>You have been assigned as the responsible person for Signature Task:</p>
                            <b>{self.cr_seq_name}</b>
                        ''',
                    'email_to': user.email,
                }

                mail = self.env['mail.mail'].create(mail_values)
                mail.send()
            except Exception as e:
                raise UserError(f"Failed to send email: {e}")
        if not self.cr_attachment:
            raise UserError(_("Please upload a PDF attachment before sending for signature."))

        api_client = self._get_docusign_api_client()

        if self.cr_docs_policy == 'simultaneously':
            envelope_definition = self._create_envelope_definition(self.cr_recipients)
            for recip in self.cr_recipients:
                recip.cr_unsigned_attachments = self.cr_attachment
                recip.cr_routing_order = 1
                recip.cr_send_status='sent'

        elif self.cr_docs_policy == 'hierarchy':
            for index, recipient in enumerate(self.cr_recipients):
                recipient.cr_routing_order = index + 1
            envelope_definition = self._create_envelope_definition(self.cr_recipients)
            self.cr_recipients[0].cr_unsigned_attachments = self.cr_attachment
            self.cr_recipients[0].cr_send_status = 'sent'

        envelopes_api = EnvelopesApi(api_client)
        try:
            envelope_summary = envelopes_api.create_envelope(self.env.user.cr_account_id,
                                                             envelope_definition=envelope_definition)

            self.cr_docusign_envelope_id = envelope_summary.envelope_id
            self.cr_status = 'sent'
            notification_message = f"Document sent for signature with Envelope ID: {envelope_summary.envelope_id}."
            self.message_post(body=notification_message, message_type='notification')
            self.cr_is_doc_sent=True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Successful'),
                    'message': _('Document(s) has been sent successfully!'),
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    },
                },
            }

        except Exception as e:
                raise UserError(_("Failed to send document for signature. Error: %s" % str(e)))

    def action_update_status(self):
        """Updates the status of the document envelope and its recipients
         based on the current state in DocuSign."""

        api_client = self._get_docusign_api_client()
        envelope_api = EnvelopesApi(api_client)

        try:
            envelope = envelope_api.get_envelope(self.env.user.cr_account_id, self.cr_docusign_envelope_id)

            account_id = self.env.user.cr_account_id
            envelope_id = self.cr_docusign_envelope_id
            recipients_response = envelope_api.list_recipients(account_id, envelope_id)
            if not recipients_response or not recipients_response.signers:
                raise UserError(_("No signers found for this envelope."))

            for recipient in recipients_response.signers:
                recipient_status = recipient.status.lower() if recipient.status else 'unknown'
                has_signed = recipient_status in ['completed', 'signed']

                matching_recip = self.cr_recipients.filtered(lambda r: r.cr_email == recipient.email)
                if matching_recip:
                    if matching_recip.cr_sign_status != ('signed' if has_signed else 'unsigned'):
                        matching_recip.cr_sign_status = 'signed' if has_signed else 'unsigned'
                        self.cr_last_signed = matching_recip.cr_email

                if self.cr_docs_policy == 'simultaneously':
                    if has_signed:
                        self.attach_sim_doc(matching_recip, recipient)

            if self.cr_docs_policy == 'hierarchy':
                last_signed_index = next(
                    (index for index, r in enumerate(self.cr_recipients) if r.cr_email == self.cr_last_signed),
                    None
                )
                next_index = last_signed_index + 1 if last_signed_index is not None else None
                next_recipient = self.cr_recipients[next_index] if next_index is not None and next_index < len(
                    self.cr_recipients) else None

                if next_recipient is not None:
                    next_recipient.cr_send_status = 'sent'
                    self.message_post(body=f"Document sent to the next recipient:")

                self._attach_signed_documents_to_next_recipient()

            self.cr_status = envelope.status

            return True

        except Exception as e:
            raise UserError(_("Failed to update document status. Error: %s" % str(e)))

    def attach_sim_doc(self, current_recipient, recipient):
        """ Attach signed documents for the current recipient from DocuSign."""

        api_client = self._get_docusign_api_client()
        envelope_api = EnvelopesApi(api_client)

        try:
            envelope_documents = envelope_api.list_documents(
                self.env.user.cr_account_id, self.cr_docusign_envelope_id
            )

            for document in envelope_documents.envelope_documents:
                if "summary" in document.name.lower():
                    continue

                # Get document as bytes directly
                document_bytes = envelope_api.get_document(
                    self.env.user.cr_account_id,
                    document.document_id,
                    self.cr_docusign_envelope_id
                )

                # Handle both file path (string) and bytes responses
                if isinstance(document_bytes, str):
                    # If it's a file path, read the file
                    with open(document_bytes, 'rb') as f:
                        document_data = f.read()
                    # Clean up temp file
                    try:
                        os.remove(document_bytes)
                    except:
                        pass
                else:
                    # If it's already bytes, use it directly
                    document_data = document_bytes

                attachment_name = f"{current_recipient.cr_name}_signed.pdf"
                existing_attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', self._name),
                    ('res_id', '=', self.id),
                    ('name', '=', attachment_name)
                ], limit=1)

                if existing_attachment:
                    existing_attachment.datas = base64.b64encode(document_data).decode('utf-8')
                else:
                    attachment = self.env['ir.attachment'].create({
                        'name': attachment_name,
                        'type': 'binary',
                        'datas': base64.b64encode(document_data).decode('utf-8'),
                        'res_model': self._name,
                        'res_id': self.id,
                        'mimetype': 'application/pdf',
                    })
                    current_recipient.cr_signed_attachments = attachment.datas

        except Exception as e:
            raise UserError(_("Failed to attach document. Error: %s" % str(e)))


    def _attach_signed_documents_to_next_recipient(self):
        """
        Attach the signed document of the last recipient to the next recipient's unsigned attachment.
        """
        api_client = self._get_docusign_api_client()
        envelope_api = EnvelopesApi(api_client)

        try:
            envelope_documents = envelope_api.list_documents(
                self.env.user.cr_account_id, self.cr_docusign_envelope_id
            )

            recipients = self.cr_recipients.sorted(key=lambda r: r.cr_routing_order or 0)

            last_signed_index = next(
                (index for index, r in enumerate(recipients) if r.cr_email == self.cr_last_signed),
                None
            )

            if last_signed_index is None:
                return

            next_index = last_signed_index + 1
            next_recipient = recipients[next_index] if next_index < len(recipients) else None

            for document in envelope_documents.envelope_documents:
                if "summary" in document.name.lower():
                    continue

                # Get document as bytes directly
                document_bytes = envelope_api.get_document(
                    self.env.user.cr_account_id,
                    document.document_id,
                    self.cr_docusign_envelope_id
                )

                # Handle both file path (string) and bytes responses
                if isinstance(document_bytes, str):
                    # If it's a file path, read the file
                    with open(document_bytes, 'rb') as f:
                        document_data = f.read()
                    # Clean up temp file
                    try:
                        os.remove(document_bytes)
                    except:
                        pass
                else:
                    # If it's already bytes, use it directly
                    document_data = document_bytes

                attachment_name = f"{recipients[last_signed_index].cr_name}_signed.pdf"

                existing_attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', self._name),
                    ('res_id', '=', self.id),
                    ('name', '=', attachment_name)
                ], limit=1)

                if existing_attachment:
                    existing_attachment.datas = base64.b64encode(document_data).decode('utf-8')
                    attachment = existing_attachment
                else:
                    attachment = self.env['ir.attachment'].create({
                        'name': attachment_name,
                        'type': 'binary',
                        'datas': base64.b64encode(document_data).decode('utf-8'),
                        'res_model': self._name,
                        'res_id': self.id,
                        'mimetype': 'application/pdf',
                    })

                recipients[last_signed_index].cr_signed_attachments = attachment.datas

                if next_recipient:
                    next_recipient.cr_unsigned_attachments = attachment.datas

        except Exception as e:
            raise UserError(_("Failed to attach signed documents. Error: %s" % str(e)))

    def _create_envelope_definition(self, recipients):
        """Create an envelope definition for DocuSign, including recipients
            and the document to be signed."""

        signers = []
        for recipient in recipients:

            sign_here_tab = SignHere(
                anchor_string="Sign Here",
                anchor_units="pixels",
                anchor_x_offset="10",
                anchor_y_offset="20"
            )

            signer = Signer(
                email=recipient.cr_email,
                name=recipient.cr_name,
                recipient_id=str(recipient.id),
                routing_order=str(recipient.cr_routing_order),
                tabs=Tabs(sign_here_tabs=[sign_here_tab])
            )
            signers.append(signer)

        document = Document(
            document_base64=self.cr_attachment.decode('utf-8'),
            name="Document to Sign",
            file_extension="pdf",
            document_id="1"
        )

        envelope_definition = EnvelopeDefinition(
            email_subject="Please sign the document",
            documents=[document],
            recipients=Recipients(signers=signers),
            status="sent"
        )

        return envelope_definition


    def action_download_doc(self):
        """Download signed documents from DocuSign and create an attachment in Odoo."""
        api_client = self._get_docusign_api_client()
        envelope_api = EnvelopesApi(api_client)

        try:
            downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
            os.makedirs(downloads_folder, exist_ok=True)

            envelope_documents = envelope_api.list_documents(
                self.env.user.cr_account_id, self.cr_docusign_envelope_id
            )

            for document in envelope_documents.envelope_documents:
                if "summary" in document.name.lower():
                    continue

                pdf_bytes = envelope_api.get_document(
                    self.env.user.cr_account_id,
                    document.document_id,
                    self.cr_docusign_envelope_id
                )

                final_file_path = os.path.join(downloads_folder, "signed.pdf")
                with open(final_file_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_bytes)

                attachment = self.env['ir.attachment'].create({
                    'name': "signed.pdf",
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_bytes).decode('utf-8'),
                    'res_model': self._name,
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })

                self.message_post(
                    body=f"Here is Your Signed Document.",
                    attachment_ids=[attachment.id]
                )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Downloaded'),
                    'message': _('Document downloaded and attached successfully.'),
                    'type': 'success',
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                }
            }

        except Exception as e:
            raise UserError(f"An error occurred while downloading the document: {str(e)}")

    def _get_docusign_api_client(self):
        """ Create and return a DocuSign API client instance based on the user's account type."""

        account_type = getattr(self.env.user, 'cr_account_type')
        api_client = ApiClient()
        if account_type == 'developer':
            api_client.host = "https://demo.docusign.net/restapi"
        else:
            api_client.host = "https://www.docusign.net/restapi"
        api_client.set_default_header("Authorization", f"Bearer {self.env.user.cr_access_token}")
        return api_client
