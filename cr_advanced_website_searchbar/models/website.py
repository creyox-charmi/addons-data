# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from psycopg2 import sql
from odoo import api, fields, models, tools, http, release, registry
from odoo.osv.expression import AND, OR, FALSE_DOMAIN, get_unaccent_wrapper
import re


class Website(models.Model):
    _inherit = "website"

    def _search_get_details(self, search_type, order, options):
        ref = super()._search_get_details(search_type, order, options)
        if search_type in ["products"]:
            ref.clear()
            if search_type in ["products", "products_only", "all"]:
                ref.append(
                    self.env["product.template"]._search_get_detail(
                        self, order, options
                    )
                )
            if search_type in ["products", "product_categories_only", "all"]:
                ref.append(
                    self.env["product.public.category"]._search_get_detail(
                        self, order, options
                    )
                )
        # Add condition to remove 'website.page' model when search_type is "all"
        if search_type in ["all"]:
            ref[:] = [item for item in ref if item.get("model") == "website.page"]
            if search_type in ["products", "products_only", "all"]:
                ref.append(
                    self.env["product.template"]._search_get_detail(
                        self, order, options
                    )
                )
            if search_type in ["products", "product_categories_only", "all"]:
                ref.append(
                    self.env["product.public.category"]._search_get_detail(
                        self, order, options
                    )
                )

        return ref

    def _search_exact(self, search_details, search, limit, order):
        if isinstance(search, str):
            pass
        else:
            search = None
        ref = super()._search_exact(search_details, search, limit, order)
        return ref

    # def _search_exact(self, search_details, search, limit, order):
    #     ref = super()._search_exact(search_details, search, limit, order)
    #     total_count = sum(entry['count'] for entry in ref[1])
    #     if total_count == 0:
    #         all_results = []
    #         total_count = 0
    #         for search_detail in search_details:
    #             model = self.env[search_detail['model']]
    #             results, count = model._search_fetch_cr(search_detail, search, limit, order)
    #             search_detail['results'] = results
    #             total_count += count
    #             search_detail['count'] = count
    #             all_results.append(search_detail)
    #
    #         return total_count, all_results
    #
    #     return ref



    def cr_search_find_fuzzy_term(
        self, search_details, search, limit=1000, word_list=None
    ):
        if (
            len(search) < 4
            or " " in search
            or len(re.findall(r"\d", search)) / len(search) >= 0.8
        ):
            return search
        search = search.lower()
        words = set()
        best_score = 0
        best_word = None
        enumerate_words = (
            self.cr_trigram_enumerate_words_cr
            if self.env.registry.has_trigram
            else self._basic_enumerate_words
        )
        x = enumerate_words(search_details, search, limit)
        for word in word_list or enumerate_words(search_details, search, limit):
            if search in word:
                return search
            if word not in words:
                words.add(word)
        return words

    def cr_trigram_enumerate_words_cr(self, search_details, search, limit):
        match_pattern = r"[\w./-]{%s,}" % min(4, len(search) - 3)
        similarity_threshold = 0.3
        lang = self.env.lang or "en_US"
        for search_detail in search_details:
            model_name, fields = search_detail["model"], search_detail["search_fields"]
            model = self.env[model_name]
            if search_detail.get("requires_sudo"):
                model = model.sudo()
            domain = search_detail["base_domain"].copy()
            fields = set(fields).intersection(model._fields)

            unaccent = get_unaccent_wrapper(self.env.cr)

            inherits_fields = {
                inherits_model_fname: {
                    "table": self.env[inherits_model_name]._table,
                    "fname": inherits_field_name,
                }
                for inherits_model_name, inherits_field_name in model._inherits.items()
                for inherits_model_fname in self.env[inherits_model_name]._fields.keys()
                if inherits_model_fname in fields
            }
            similarities = []
            for field in fields:
                # Field might belong to another model (`inherits` mechanism)
                table = (
                    inherits_fields[field]["table"]
                    if field in inherits_fields
                    else model._table
                )
                similarities.append(
                    sql.SQL("word_similarity({search}, {field})").format(
                        search=unaccent(sql.Placeholder("search")),
                        field=unaccent(
                            sql.SQL("{table}.{field}").format(
                                table=sql.Identifier(table), field=sql.Identifier(field)
                            )
                        )
                        if not model._fields[field].translate
                        else unaccent(
                            sql.SQL(
                                "COALESCE({table}.{field}->>{lang}, {table}.{field}->>'en_US')"
                            ).format(
                                table=sql.Identifier(table),
                                field=sql.Identifier(field),
                                lang=sql.Literal(lang),
                            )
                        ),
                    )
                )
            best_similarity = sql.SQL("GREATEST({similarities})").format(
                similarities=sql.SQL(", ").join(similarities)
            )
            where_clause = sql.SQL("")
            # Filter unpublished records for portal and public user for
            # performance.
            # TODO: Same for `active` field?
            filter_is_published = (
                "is_published" in model._fields
                and model._fields["is_published"].base_field.model_name == model_name
                and not self.env.user.has_group("base.group_user")
            )
            if filter_is_published:
                where_clause = sql.SQL("WHERE is_published")

            from_clause = sql.SQL("FROM {table}").format(
                table=sql.Identifier(model._table)
            )
            # Specific handling for fields being actually part of another model
            # through the `inherits` mechanism.
            for table_to_join in {
                field["table"]: field["fname"] for field in inherits_fields.values()
            }.items():  # Removes duplicate inherits model
                from_clause = sql.SQL(
                    """
                    {from_clause}
                    LEFT JOIN {inherits_table} ON {table}.{inherits_field} = {inherits_table}.id
                """
                ).format(
                    from_clause=from_clause,
                    table=sql.Identifier(model._table),
                    inherits_table=sql.Identifier(table_to_join[0]),
                    inherits_field=sql.Identifier(table_to_join[1]),
                )
            query = sql.SQL(
                """
                SELECT {table}.id, {best_similarity} AS _best_similarity
                {from_clause}
                {where_clause}
                ORDER BY _best_similarity desc
                LIMIT 1000
            """
            ).format(
                table=sql.Identifier(model._table),
                best_similarity=best_similarity,
                from_clause=from_clause,
                where_clause=where_clause,
            )
            self.env.cr.execute(query, {"search": search})

            ids = {row[0] for row in self.env.cr.fetchall() if row[1] and row[1] > 0}
            domain.append([("id", "in", list(ids))])
            domain = AND(domain)
            records = model.search_read(domain, fields, limit=limit)
            for record in records:
                for field, value in record.items():
                    if isinstance(value, str):
                        value = value.lower()
                        yield from re.findall(match_pattern, value)

    def _search_render_results(self, search_details, limit):
        # Call the original method
        search_details = super()._search_render_results(search_details, limit)

        # Get blocked words from the current user's company
        company = self.env.company
        blocked_words = set(
            word.name.lower() for word in company.add_words_ids if word.name
        )

        for search_detail in search_details:
            results_data = search_detail.get("results_data", [])
            results = search_detail.get("results", self.env["product.template"])

            if results._name == "product.template":
                filtered_results = []
                filtered_data = []
                for rec, data in zip(results, results_data):
                    if not self._has_blocked_words(rec, blocked_words):
                        filtered_results.append(rec)
                        filtered_data.append(data)
                search_detail["results"] = self.env["product.template"].browse(
                    [r.id for r in filtered_results]
                )
                search_detail["results_data"] = filtered_data

        return search_details

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
        # Tags and variants
        fields_to_check.extend([tag.name for tag in rec.product_tag_ids])
        fields_to_check.extend([variant.name for variant in rec.product_variant_ids])

        for val in fields_to_check:
            val_lower = val.lower()
            if any(word in val_lower for word in blocked_words):
                return True
        return False
