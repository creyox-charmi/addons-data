# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import random
from odoo import api, fields, models
from odoo.tools import escape_psql
from odoo.osv import expression


class WebsiteSearchableMixin(models.AbstractModel):
    _inherit = 'website.searchable.mixin'

    @api.model
    def _search_fetch_cr(self, search_detail, search, limit, order):
        model = self.sudo() if search_detail.get('requires_sudo') else self
        ref = (self._get_random_records(model, 5), 5)
        return ref

    @api.model
    def _search_fetch(self, search_detail, search, limit, order):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>search : ',search)
        # if isinstance(search, set):
        #     fields = search_detail['search_fields']
        #     base_domain = search_detail['base_domain']
        #
        #     model = self.sudo() if search_detail.get('requires_sudo') else self
        #     final_result = model.browse()
        #     results = model.search([])
        #     for field in fields:
        #         for result in results:
        #             name = getattr(result, field, None)
        #             if name:
        #                 for data in search:
        #                     if data in name.lower():
        #                         if result not in final_result:
        #                             final_result |= result
        #
        #     count = len(final_result)
        #     return final_result, count

        ref = super()._search_fetch(search_detail, search, limit, order)
        print("////////")
        print("ref : ",ref)
        # Get the model being searched (e.g., 'product.template')
        if search:
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@1")
            results = ref[0]
            count = ref[1]
            model_name = search_detail.get('model')
            if model_name == 'product.template':
                blocked_words = set(w.name.lower() for w in self.env.company.add_words_ids if w.name)

                filtered_results = results.filtered(
                    lambda rec: not self._has_blocked_words(rec, blocked_words)
                )
                print('len(filtered_results) : ',len(filtered_results))
                ref = (filtered_results, len(filtered_results))


        if search and ref[1] != 0:
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2")
            ids = ref[0].ids
            model = self.sudo() if search_detail.get('requires_sudo') else self
            fields = search_detail['search_fields']
            final_data = model.browse()
            for field in fields:
                for id in ids:
                    data = model.search([('id', '=', id)])
                    if getattr(data, field, None):
                        value = getattr(data, field, None)
                        if search.lower() in value.lower():
                            if data not in final_data:
                                final_data |= data

            count = len(final_data)
            print('count : ',count)
            ref = (final_data, count)
            # return final_data, count
        return ref

    def _has_blocked_words(self, rec, blocked_words):
        """
        Checks if any product.template field contains blocked words.
        """
        fields_to_check = [
            rec.name or '',
            rec.default_code or '',
            rec.description or '',
            rec.description_sale or '',
        ]
        fields_to_check.extend([tag.name for tag in rec.product_tag_ids])
        fields_to_check.extend([variant.name for variant in rec.product_variant_ids])
        fields_to_check.extend([variant.default_code for variant in rec.product_variant_ids])

        for val in fields_to_check:
            if val:
                print('val : ',val)
                val_lower = val.lower()
                if any(word in val_lower for word in blocked_words):
                    return True
        return False

    def _get_random_records(self, model, limit):
        """Fetches `limit` random records from the given model."""
        all_ids = model.search([]).ids  # Get all record IDs
        random_ids = random.sample(all_ids, min(len(all_ids), limit))  # Pick random ones
        return model.browse(random_ids) if random_ids else model.browse()
