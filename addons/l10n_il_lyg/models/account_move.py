# -*- coding: utf-8 -*-
# Copyright (C) Gilliam Management Services and Information Systems, Ltd. (the owner of Bizzup), 2021, 2022, 2023, 2024, 2025
# All Rights Reserved to Gilliam Management Services and Information Systems, Ltd.
# Unauthorized copying, editing or printing of this file, in any way is strictly prohibited
# Proprietary and confidential for more information, please contact
# lg@bizzup.app

from odoo import models, fields, _
from odoo.http import request
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_original_printed = fields.Boolean(
        default=False,
        help="Technical field used to display 'Original' on first pdf print")

    def consume_original_print(self):
        """
        Inform if original pdf has been printed and mark it as printed if it wasn't already the case.
        Only a posted invoice can consume the original print

        :return: True the first time, False otherwise
        """
        if self.state != 'posted' or self.is_original_printed:
            return False
        self.is_original_printed = True
        return True

    def _reverse_moves(self, default_values_list=None, cancel=False):
        # OVERRIDE to pass value of consume_original_print as false
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'is_original_printed': False, })
        return super()._reverse_moves(default_values_list=default_values_list,
                                      cancel=cancel)

    def unlink(self):
        for rec in self:
            if rec.state == 'posted':
                raise ValidationError(
                    _('You can not delete posted record.'))
        return super(AccountMove, self).unlink()

    def button_draft(self):
        if self.state == 'posted':
            raise ValidationError(
                _('You can not Reset to draft if record is posted.'))
        return super(AccountMove, self).button_draft()

    def action_post(self):
        res = super(AccountMove, self).action_post()
        icpsudo = request.env['ir.config_parameter'].sudo()
        vat_limit = icpsudo.get_param(
            "l10n_il_lyg.vat_limit"
        )
        for rec in self:
            if ((rec.partner_id and rec.partner_id.company_type == 'company'
                    and not rec.partner_id.vat) and
                    rec.partner_id.country_code == 'IL'):
                raise ValidationError(
                    _("Please insert VAT ID on the selected Customer/Vendor."))
            if (rec.partner_id and not rec.partner_id.vat and
                    rec.amount_total > int(vat_limit) and
                    rec.partner_id.country_code == 'IL'
            ):
                raise ValidationError(
                    _("Please insert VAT ID on the selected Customer/Vendor."))
        return res
