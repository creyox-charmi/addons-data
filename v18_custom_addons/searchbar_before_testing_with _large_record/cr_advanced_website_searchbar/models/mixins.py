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
            model = self.sudo() if search_detail.get("requires_sudo") else self
            fields = search_detail["search_fields"]
            final_data = model.browse()
            for field in fields:
                for id in ids:
                    data = model.search([("id", "=", id)])
                    if field == "product_tag_ids.name":
                        tags = data.product_tag_ids
                        for tag in tags:
                            tag_name = tag.name
                            if search.lower() in tag_name.lower():
                                if data not in final_data:
                                    final_data |= data

                    if getattr(data, field, None):
                        value = getattr(data, field, None)
                        if search.lower() in value.lower():
                            if data not in final_data:
                                final_data |= data
            count = len(final_data)
            ref = (final_data, count)
        return ref

    def _search_build_domain(self, domain_list, search, fields, extra=None):
        """
        Builds a search domain by combining a base domain with partial matches
        of each term in the search expression against given fields.

        If search is a set, it is ignored and only the base domain is returned.
        """
        domains = domain_list.copy()

        # Skip if search is a set
        if search and not isinstance(search, set):
            search_terms = search.split()
            for search_term in search_terms:
                subdomains = [[(field, 'ilike', escape_psql(search_term))] for field in fields]
                if extra:
                    extra_domain = extra(self.env, search_term)
                    if extra_domain:
                        subdomains.append(extra_domain)
                domains.append(expression.OR(subdomains))

        return expression.AND(domains)

    def _get_random_records(self, model, limit):
        """Fetches `limit` random records from the given model."""
        all_ids = model.search([]).ids  # Get all record IDs
        random_ids = random.sample(all_ids, min(len(all_ids), limit))  # Pick random ones
        return model.browse(random_ids) if random_ids else model.browse()
