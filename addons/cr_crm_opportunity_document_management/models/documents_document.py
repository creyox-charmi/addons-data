# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Document(models.Model):
    _inherit = 'documents.document'

    is_master_folder = fields.Boolean(string="Master Folder", default=False, help="Indicates if this folder is a master folder and cannot be renamed.")

    def write(self, vals):
        if 'name' in vals and not self.env.context.get('bypass_master_folder_check'):
            for record in self:
                if record.is_master_folder:
                    raise ValidationError(_("The name of a master folder cannot be changed."))
        return super(Document, self).write(vals)