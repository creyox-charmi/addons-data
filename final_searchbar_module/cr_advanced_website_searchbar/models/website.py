# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import re
from psycopg2 import sql
from odoo import api, fields, models, tools, http, release, registry
from odoo.osv.expression import AND, OR, FALSE_DOMAIN, get_unaccent_wrapper


class CrWebsite(models.Model):
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
