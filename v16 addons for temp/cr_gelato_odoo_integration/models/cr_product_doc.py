# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ProductDoc(models.Model):
    _name = 'cr.product.doc'
    _description = "Product Doc"
    _inherits = {
        'ir.attachment': 'ir_attachment_id',
    }

    ir_attachment_id = fields.Many2one(
        'ir.attachment',
        string="Attachment",
        required=True,
        ondelete='cascade')

    active = fields.Boolean(default=True)


    def create(self, vals_list):
        ref = super(ProductDoc,self.with_context(disable_product_documents_creation=True),).create(vals_list)
        return ref

    def copy(self, default=None):
        default = default or {}

        attachment_fields = self.env['ir.attachment']._fields
        filtered_defaults = {
            key: value for key, value in default.items()
            if key in attachment_fields
        }

        new_attachment = self.ir_attachment_id.with_context(
            no_document=True,
            disable_product_documents_creation=True,
        ).copy(filtered_defaults)

        default['ir_attachment_id'] = new_attachment.id
        return super().copy(default)

    def unlink(self):
        attach = self.ir_attachment_id
        ref = super().unlink()
        return ref and attach.unlink()
