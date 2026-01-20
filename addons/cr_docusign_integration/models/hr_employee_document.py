# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api
import hashlib

class HrEmployeeDocument(models.Model):
    _inherit = 'hr.employee.document'

    def _get_binary_hash(self, binary_data):
        """Return hash of binary data (base64 string)."""
        if not binary_data:
            return None
        if isinstance(binary_data, str):
            binary_data = binary_data.encode()  # ensure bytes
        return hashlib.sha1(binary_data).hexdigest()

    def action_get_signature(self):
        """Open the signature window for the current employee document."""
        self.ensure_one()

        domain = [('cr_hr_employee_document_id', '=', self.id)]
        Signature = self.env['cr.signature']

        # Hashes of existing binary data in cr.signature
        existing_hashes = [
            self._get_binary_hash(b) for b in Signature.search(domain).mapped('cr_attachment')
        ]

        for attachment in self.doc_attachment_id:
            att_hash = self._get_binary_hash(attachment.datas)

            if att_hash not in existing_hashes:
                self.env['cr.signature'].create({
                    'cr_hr_employee_document_id': self.id,
                    'cr_model_reference': 'HR Employee Documents',
                    'cr_attachment': attachment.datas,
                })
            else:
                print(f"[DEBUG] Attachment {attachment.id} already exists (same binary), skipping...")

        action = {
            'name': 'Signature',
            'type': 'ir.actions.act_window',
            'res_model': 'cr.signature',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': domain,
        }
        return action

