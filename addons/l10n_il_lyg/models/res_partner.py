# -*- coding: utf-8 -*-
# Copyright (C) Gilliam Management Services and Information Systems, Ltd. (the owner of Bizzup), 2021, 2022, 2023, 2024, 2025
# All Rights Reserved to Gilliam Management Services and Information Systems, Ltd.
# Unauthorized copying, editing or printing of this file, in any way is strictly prohibited
# Proprietary and confidential for more information, please contact
# lg@bizzup.app

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_il_ita_branch = fields.Many2one('l10n.il.ita.branch',
                                         string='ITA Branch',
                                         help="This field contains the ITA branch that expended the withholding tax "
                                              "rate and that will be used for Annual Witholding Tax Report")
    l10n_il_income_tax_id_number = fields.Char(string='IncomeTax ID')
    l10n_il_registry_number = fields.Char(string='Registry Number')
