# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """Overriding the _search method to modify how products are searched"""
        # Getting the current user object
        user = self.env.user

        # Referencing the specific restricted group for product access
        restricted_group = self.env.ref(
            "cr_product_restric_user.cr_product_restriction_on_user"
        )

        # Check if the user belongs to the restricted group
        if restricted_group in user.groups_id:

            # If the user's restriction type is 'product', filter by specific products
            if user.cr_restriction_on == "product":
                product_ids = user.cr_product_template_ids.ids
                if product_ids:
                    # Modify the search arguments to filter products by the allowed product IDs
                    args.append(("id", "in", product_ids))

            # If the user's restriction type is 'category', filter by specific product categories
            if user.cr_restriction_on == "category":
                category_ids = user.cr_product_category_ids.ids
                if category_ids:
                    # Modify the search arguments to filter products by the allowed category IDs
                    args.append(("categ_id", "in", category_ids))

        # Call the original _search method with the modified arguments
        return super(ProductTemplate, self)._search(
            args, offset, limit, order, count, access_rights_uid
        )


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """Overriding the _search method to modify how products are searched"""
        # Getting the current user object
        user = self.env.user

        # Referencing the specific restricted group for product access
        restricted_group = self.env.ref(
            "cr_product_restric_user.cr_product_restriction_on_user"
        )

        # Check if the user belongs to the restricted group
        if restricted_group in user.groups_id:

            # If the user's restriction type is 'product', filter by specific products
            if user.cr_restriction_on == "product":
                template_ids = user.cr_product_template_ids.ids
                if template_ids:
                    # Modify the search arguments to filter products by the allowed product IDs
                    args.append(("product_tmpl_id", "in", template_ids))

            # If the user's restriction type is 'category', filter by specific product categories
            if user.cr_restriction_on == "category":
                category_ids = user.cr_product_category_ids.ids
                if category_ids:
                    # Modify the search arguments to filter products by the allowed category IDs
                    args.append(("categ_id", "in", category_ids))

        # Call the original _search method with the modified arguments
        return super(Product, self)._search(
            args, offset, limit, order, count, access_rights_uid
        )
