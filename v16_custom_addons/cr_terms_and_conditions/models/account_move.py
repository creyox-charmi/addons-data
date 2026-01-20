# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api , _
from googletrans import Translator, constants
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    cr_account_move_terms_and_condition_id = fields.Many2one(comodel_name='cr.terms.and.condition',
                                                             string='Terms and Condition')

    @api.onchange('partner_id')
    def add_name(self):
        """
        Automatically fetch and set the Terms and Conditions based on the selected partner.
        If no specific T&C is found, fallback to the default T&C.
        """
        if self.partner_id:
            line = self.env['cr.terms.and.condition'].search(
                [
                    ('customer', 'in', self.partner_id.id),
                    ('cr_model_reference', '=', 'invoice')
                ], limit=1)
            if line:
                self.cr_account_move_terms_and_condition_id = line.id
            else:
                # Fallback to default T&C if none found
                self.default_t_and_c()

    def default_t_and_c(self):
        """
        Set default Terms and Conditions based on company settings.
        If a boolean flag is set, use the default T&C from the company.
        """
        is_terms_and_condition = self.env.user.company_id.cr_is_boolean_for_account_move
        cr_default_terms_and_condition = self.env.user.company_id.cr_account_move_terms_and_conditions_id
        if is_terms_and_condition:
            if cr_default_terms_and_condition:
                self.cr_account_move_terms_and_condition_id = cr_default_terms_and_condition.id
            else:
                self.cr_account_move_terms_and_condition_id = None
        else:
            self.cr_account_move_terms_and_condition_id = None

    @api.onchange('partner_id', 'cr_account_move_terms_and_condition_id')
    def add_note(self):
        """
        Set the note field based on the selected Terms and Conditions.
        If the customer language differ, translate the note if automatic translation is enabled.
        """
        if self.partner_id:
            source_language = self.cr_account_move_terms_and_condition_id.language
            destination_language = self.partner_id.lang
            notes = self.cr_account_move_terms_and_condition_id.terms_and_condition

            # No translation needed
            if source_language == destination_language:
                self.narration = notes
            else:
                if self.env.user.company_id.cr_is_auto_translate_for_account_move:
                    self.translate_language(source_language, destination_language, notes)
                else:
                    # Set notes without translation if not enabled
                    self.narration = notes

    def translate_language(self, source_language, destination_language, notes):
        """
       Translate the Terms and Conditions from the source language to the destination language.
       Raises a UserError if the language is not supported.
       """
        # Get available languages
        dic = constants.LANGUAGES
        source_code = self.get_source_code(source_language)
        destination_code = self.get_destination_code(destination_language)

        if source_code in dic.keys() and destination_code in dic.keys():
            # Initialize translator
            translator = Translator()
            translations = translator.translate(notes, src=source_code, dest=destination_code)
            # Set the translated note
            self.narration = translations.text
        else:
            # Raise an error if the languages are unsupported
            if source_code not in dic.keys():
                raise UserError(_(f"{source_language} is not supported"))
            if destination_code not in dic.keys():
                raise UserError(_(f"{destination_language} is not supported"))

    def get_source_code(self, source_language):
        """
        Convert the source language into a code compatible with the translation library.
        """
        s_code = source_language.split("_")
        source_code = s_code[0]

        # Handle special cases for language codes
        if source_code == 'sr@latin':
            source_code = 'sr'
        elif source_code == 'nb':
            source_code = 'no'
        elif source_language == 'zh_HK':
            source_code = 'zh-cn'
        elif source_language == 'zh_CN':
            source_code = 'zh-cn'
        elif source_language == 'zh_TW':
            source_code = 'zh-tw'
        return source_code

    def get_destination_code(self, destination_language):
        """
        Convert the destination language into a code compatible with the translation library.
        """
        d_code = destination_language.split("_")
        destination_code = d_code[0]

        # Handle special cases for language codes
        if destination_code == 'sr@latin':
            destination_code = 'sr'
        elif destination_code == 'nb':
            destination_code = 'no'
        elif destination_language == 'zh_HK':
            destination_code = 'zh-cn'
        elif destination_language == 'zh_CN':
            destination_code = 'zh-cn'
        elif destination_language == 'zh_TW':
            destination_code = 'zh-tw'
        return destination_code
