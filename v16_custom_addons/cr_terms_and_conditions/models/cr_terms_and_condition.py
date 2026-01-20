# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import api, fields, models, _


@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()


class TermsAndCondition(models.Model):
    _name = "cr.terms.and.condition"
    _description = "Terms_Conditions"

    name = fields.Char(string='Name', required=True)
    terms_and_condition = fields.Html(string='Teams and Condition', required=True)
    customer = fields.Many2many('res.partner', string='Customer')
    language = fields.Selection(_lang_get, string='Language', required=True)
    cr_model_reference = fields.Selection((
        [
            ('sales', 'Sales'),
            ('purchase', 'Purchase'),
            ('invoice', 'Invoice')
        ]
    ), string='Model Reference', required=True)
