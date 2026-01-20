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
        if isinstance(search, set):
            fields = search_detail['search_fields']
            base_domain = search_detail['base_domain']

            model = self.sudo() if search_detail.get('requires_sudo') else self
            final_result = model.browse()
            results = model.search([])
            for field in fields:
                for result in results:
                    name = getattr(result, field, None)
                    if name:
                        for data in search:
                            if data in name.lower():
                                if result not in final_result:
                                    final_result |= result

            count = len(final_result)
            return final_result, count

        ref = super()._search_fetch(search_detail, search, limit, order)
        if search and ref[1] != 0:
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
            return final_data, count
        return ref

    def _get_random_records(self, model, limit):
        """Fetches `limit` random records from the given model."""
        all_ids = model.search([]).ids  # Get all record IDs
        random_ids = random.sample(all_ids, min(len(all_ids), limit))  # Pick random ones
        return model.browse(random_ids) if random_ids else model.browse()
