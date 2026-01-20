# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TermsCondition(models.Model):
    _name = 'terms.condition'
    _description = 'Terms and Conditions'
    _order = 'sequence, id'

    name = fields.Char('Title', required=True)
    description = fields.Html('Description', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    is_default = fields.Boolean('Is Default', default=False)

    @api.model
    def get_active_terms(self):
        """Get active terms and conditions"""
        return self.search([('active', '=', True)], order='sequence, id', limit=1)
