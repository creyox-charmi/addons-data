# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class SettingConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    cr_customer_account = fields.Selection(
        related="company_id.cr_customer_account", readonly=False,
        selection=[
            ('on_invitation', 'On Invitation'),
            ('free_sign_up', 'Free Sign Up'),
        ],
        string = 'Customer Account'
    )



class ResCompany(models.Model):
    _inherit = "res.company"

    cr_customer_account = fields.Selection(
        selection=[
            ('on_invitation', 'On Invitation'),
            ('free_sign_up', 'Free Sign Up'),
        ],
        string='Customer Account'
    )