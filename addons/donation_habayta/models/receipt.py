# Copyright (C) 2021 Yves Goldberg - Ygol InternetWork - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
##############################################################################

from odoo import fields, models


class AccountReceipt(models.Model):
    _inherit = 'lyg.account.receipt'

    # ====Link Tracker=====#
    utm_source_id = fields.Many2one('utm.source', ondelete='cascade', string="Source")
    utm_campaign_id = fields.Many2one('utm.campaign', string='UTM Campaign')
    utm_medium_id = fields.Many2one('utm.medium', string="Medium")

    # ===========link with community===========
    bu_community_id = fields.Many2one('bu_community',string="Community")