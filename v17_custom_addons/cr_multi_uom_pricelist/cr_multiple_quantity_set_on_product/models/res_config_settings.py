# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    multi_quantity_on_multi_product = fields.Boolean(
        string='Multiple Quantity for Multiple Website',
        related="company_id.multi_quantity_on_multi_product",
        store=True,
        readonly=False
        )

class ResCompany(models.Model):
    _inherit = "res.company"

    multi_quantity_on_multi_product = fields.Boolean('Multiple Quantity for Multiple Website', store=True)




    

