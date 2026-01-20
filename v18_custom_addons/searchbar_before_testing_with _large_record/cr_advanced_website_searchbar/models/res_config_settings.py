# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, models, fields, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cr_name = fields.Integer(related='company_id.cr_name',string='Name',readonly=False)
    internal_reference = fields.Integer(related='company_id.internal_reference',string='Internal Reference',readonly=False)
    description = fields.Integer(related='company_id.description',string='Description',readonly=False)
    website_description = fields.Integer(related='company_id.website_description',string='Website Description',readonly=False)
    tags = fields.Integer(related='company_id.tags',string='Tags',readonly=False)
    attributes = fields.Integer(related='company_id.attributes',string='Attributes',readonly=False)

class Company(models.Model):
    _inherit = 'res.company'

    cr_name = fields.Integer(string='Name')
    internal_reference = fields.Integer(string='Internal Reference')
    description = fields.Integer(string='Description')
    website_description = fields.Integer(string='Website Description')
    tags = fields.Integer(string='Tags')
    attributes = fields.Integer(string='Attributes')
