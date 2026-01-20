# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class SettingConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company')
    cr_is_boolean_for_sale_order = fields.Boolean(string='Default Term(s) & Condition(s)', related="company_id.cr_is_boolean_for_sale_order",
                                   readonly=False)
    cr_is_boolean_for_account_move = fields.Boolean(related="company_id.cr_is_boolean_for_account_move", readonly=False)
    cr_is_boolean_for_purchase_order = fields.Boolean(related="company_id.cr_is_boolean_for_purchase_order",
                                                      readonly=False)
    cr_sale_order_terms_and_condition_id = fields.Many2one(comodel_name='cr.terms.and.condition',
                                                     related="company_id.cr_sale_order_terms_and_condition_id",
                                                     readonly=False)
    cr_account_move_terms_and_conditions_id = fields.Many2one(comodel_name='cr.terms.and.condition',
                                                              related="company_id.cr_account_move_terms_and_conditions_id",
                                                              readonly=False)
    cr_purchase_order_terms_and_conditions_id = fields.Many2one(comodel_name='cr.terms.and.condition',
                                                                related="company_id.cr_purchase_order_terms_and_conditions_id",
                                                                readonly=False)
    cr_is_auto_translate_for_sale_order = fields.Boolean(string="Auto Translate", related="company_id.cr_is_auto_translate_for_sale_order",
                                          readonly=False)
    cr_is_auto_translate_for_account_move = fields.Boolean(string="Auto Translate",
                                                           related="company_id.cr_is_auto_translate_for_account_move",
                                                           readonly=False)
    cr_is_auto_translate_for_purchase_order = fields.Boolean(string="Auto Translate",
                                                             related="company_id.cr_is_auto_translate_for_purchase_order",
                                                             readonly=False)


class ResCompany(models.Model):
    _inherit = "res.company"

    cr_is_boolean_for_sale_order = fields.Boolean(string='Default Term(s) & Condition(s)')
    cr_is_boolean_for_account_move = fields.Boolean()
    cr_is_boolean_for_purchase_order = fields.Boolean()
    cr_sale_order_terms_and_condition_id = fields.Many2one(comodel_name='cr.terms.and.condition')
    cr_account_move_terms_and_conditions_id = fields.Many2one(comodel_name='cr.terms.and.condition')
    cr_purchase_order_terms_and_conditions_id = fields.Many2one(comodel_name='cr.terms.and.condition')
    cr_is_auto_translate_for_sale_order = fields.Boolean(string="Auto Translate")
    cr_is_auto_translate_for_account_move = fields.Boolean(string="Auto Translate")
    cr_is_auto_translate_for_purchase_order = fields.Boolean(string="Auto Translate")
