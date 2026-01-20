# -*- coding: utf-8 -*-
# Copyright (C) Gilliam Management Services and Information Systems, Ltd. (the owner of Bizzup), 2021, 2022, 2023, 2024, 2025
# All Rights Reserved to Gilliam Management Services and Information Systems, Ltd.
# Unauthorized copying, editing or printing of this file, in any way is strictly prohibited
# Proprietary and confidential for more information, please contact
# lg@bizzup.app

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class WithhReason(models.Model):
    _name = 'l10n.il.tax.reason'
    _description = "Tax Reason"

    name = fields.Char(string='Withh Tax Reason')
    code = fields.Char(string='Code for Withh Tax Reason')

    @api.constrains('code', 'name')
    def _check_unique_code_name(self):
        """Ensure that the combination of code + name is unique."""
        for record in self:
            if not record.code and not record.name:
                continue  # allow multiple blanks (same as old SQL UNIQUE)
            domain = [
                ('id', '!=', record.id),
                ('code', '=', record.code),
                ('name', '=', record.name),
            ]
            if self.sudo().search_count(domain):
                raise ValidationError(
                    _("The code of the Withholding Tax Reason must be unique!")
                )
