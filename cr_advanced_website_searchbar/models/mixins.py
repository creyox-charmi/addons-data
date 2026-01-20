# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import random
from odoo import api, fields, models
from odoo.tools import escape_psql
from odoo.osv import expression


class WebsiteSearchableMixin(models.AbstractModel):
    _inherit = "website.searchable.mixin"

    @api.model
    def _search_fetch_cr(self, search_detail, search, limit, order):
        model = self.sudo() if search_detail.get("requires_sudo") else self
        ref = (self._get_random_records(model, 5), 5)
        return ref

    @api.model
    def _search_fetch(self, search_detail, search, limit, order):
        fields = search_detail["search_fields"]
        base_domain = search_detail["base_domain"]
        domain = self._search_build_domain(
            base_domain, search, fields, search_detail.get("search_extra")
        )
        model = self.sudo() if search_detail.get("requires_sudo") else self
        results = model.search(domain, order=search_detail.get("order", order))
        count = model.search_count(domain)
        ref = results, count

        if search:
            results = ref[0]
            count = ref[1]
            model_name = search_detail.get("model")
            if model_name == "product.template":
                blocked_words = set(
                    w.name.lower() for w in self.env.company.add_words_ids if w.name
                )

                filtered_results = results.filtered(
                    lambda rec: not self._has_blocked_words(rec, blocked_words)
                )
                ref = (filtered_results, len(filtered_results))

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

    def _has_blocked_words(self, rec, blocked_words):
        """
        Checks if any product.template field contains blocked words.
        """
        fields_to_check = [
            rec.name or "",
            rec.default_code or "",
            rec.description or "",
            rec.description_sale or "",
        ]
        fields_to_check.extend([tag.name for tag in rec.product_tag_ids])
        fields_to_check.extend([variant.name for variant in rec.product_variant_ids])
        fields_to_check.extend(
            [variant.default_code for variant in rec.product_variant_ids]
        )

        for val in fields_to_check:
            if val:
                val_lower = val.lower()
                if any(word in val_lower for word in blocked_words):
                    return True
        return False

    def _get_random_records(self, model, limit):
        """Fetches `limit` random records from the given model."""
        all_ids = model.search([]).ids  # Get all record IDs
        random_ids = random.sample(
            all_ids, min(len(all_ids), limit)
        )  # Pick random ones
        return model.browse(random_ids) if random_ids else model.browse()
