# -*- coding: utf-8 -*-
# Copyright (C) Gilliam Management Services and Information Systems, Ltd. (the owner of Bizzup), 2021, 2022, 2023, 2024, 2025
# All Rights Reserved to Gilliam Management Services and Information Systems, Ltd.
# Unauthorized copying, editing or printing of this file, in any way is strictly prohibited
# Proprietary and confidential for more information, please contact
# lg@bizzup.app

from odoo import fields, models


class WithhTaxReportData(models.Model):
    _inherit = 'account.tax'

    l10n_il_tax_reason = fields.Many2one('l10n.il.tax.reason',
                                         string='Tax Reason',
                                         help="This field contains the withholding tax reason that will be used for "
                                              "Annual Witholding Tax Report'")
