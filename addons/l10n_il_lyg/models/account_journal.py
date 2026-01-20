# -*- coding: utf-8 -*-
# Copyright (C) Gilliam Management Services and Information Systems, Ltd. (the owner of Bizzup), 2021, 2022, 2023, 2024, 2025
# All Rights Reserved to Gilliam Management Services and Information Systems, Ltd.
# Unauthorized copying, editing or printing of this file, in any way is strictly prohibited
# Proprietary and confidential for more information, please contact
# lg@bizzup.app

from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_l10n_installed = fields.Boolean(related="company_id.is_l10n_installed")

    @api.onchange('type')
    def _onchange_mode_type_hash_table(self):
        """Added onchange to make hash table true for Bank and Cash type Journal"""
        if self.is_l10n_installed:
            if self.type and self.type not in ['bank', 'cash']:
                self.restrict_mode_hash_table = True
