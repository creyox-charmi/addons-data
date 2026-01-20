# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import random
from odoo import api, fields, models
from odoo.tools import escape_psql
from odoo.osv import expression
from odoo.osv.expression import OR
import logging

_logger = logging.getLogger(__name__)


class WebsiteSearchableMixin(models.AbstractModel):
    _inherit = "website.searchable.mixin"

    @api.model
    def _search_fetch(self, search_detail, search, limit, order):
        model = self.sudo() if search_detail.get("requires_sudo") else self
        fields = search_detail["search_fields"]
        base_domain = search_detail["base_domain"]

        if isinstance(search, set):
            search_lower_set = {s.lower() for s in search}
            domain_clauses = []

            for s in search_lower_set:
                single_clause = []
                for field in fields:
                    single_clause.append((field, "ilike", s))
                domain_clauses.append(["|"] * (len(single_clause) - 1) + single_clause)

            # Combine all clauses using OR safely
            combined_domain = base_domain
            for clause in domain_clauses:
                combined_domain = OR([combined_domain, clause])

            results = model.search(combined_domain, limit=limit, order=order)
            return results, len(results)

        # For normal string searches — use super and additional filter
        ref = super()._search_fetch(search_detail, search, limit, order)

        if search and ref[1] != 0:
            search_lower = search.lower()
            records = self.browse(ref[0].ids)
            final_ordered_data = self.browse()

            for field in fields:
                for record in records:
                    if record in final_ordered_data:
                        continue  # Skip already matched record from a higher-priority field

                    try:
                        value = record
                        for part in field.split("."):
                            value = getattr(value, part, None)
                            if value is None:
                                break

                        if value:
                            if isinstance(value, models.Model):
                                value = ", ".join(value.mapped("name"))

                            if isinstance(value, str) and search_lower in value.lower():
                                final_ordered_data |= record
                    except Exception as e:
                        _logger.warning(
                            "Error checking field '%s' on record %s: %s",
                            field,
                            record.id,
                            str(e),
                        )

        else:
            return ref

        return final_ordered_data, len(final_ordered_data)

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
                subdomains = [
                    [(field, "ilike", escape_psql(search_term))] for field in fields
                ]
                if extra:
                    extra_domain = extra(self.env, search_term)
                    if extra_domain:
                        subdomains.append(extra_domain)
                domains.append(expression.OR(subdomains))

        return expression.AND(domains)
