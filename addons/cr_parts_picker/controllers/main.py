# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import http
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from copy import deepcopy

import logging

_logger = logging.getLogger(__name__)


class CrPartsPicker(WebsiteSale):
    @http.route(
        ["/parts-picker/category/<int:category_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def parts_picker_category(self, category_id, **post):
        Category = request.env["product.public.category"].sudo()
        ProductVariant = request.env["product.product"].sudo()

        category = Category.browse(category_id)

        # Filter child categories with is_show_in_parts_picker = True
        visible_children = category.child_id.filtered(
            lambda c: c.is_show_in_parts_picker
        )

        if visible_children:
            return request.render(
                "cr_parts_picker.child_categories_tree",
                {"parent_category": category, "child_categories": visible_children},
            )

        else:
            # Get variants whose template has this category
            variants = ProductVariant.sudo().search(
                [("product_tmpl_id.public_categ_ids", "in", category.id),("product_tmpl_id.website_published", "=", True)]
            )

            # Compute min and max price range for all variants before filtering
            min_price_range = min(variants.mapped("list_price")) if variants else 0
            max_price_range = max(variants.mapped("list_price")) if variants else 1000

            # Parse selected attributes like ['1-5', '2-9']
            selected_attribs = (
                post.getlist("attrib")
                if hasattr(post, "getlist")
                else post.get("attrib", [])
            )
            if isinstance(selected_attribs, str):
                selected_attribs = [selected_attribs]

            attrib_value_ids = []
            for attrib_pair in selected_attribs:
                try:
                    _, value_id = attrib_pair.split("-")
                    attrib_value_ids.append(int(value_id))
                except Exception:
                    continue

            if attrib_value_ids:
                # Keep variants that have all selected attribute values
                variants = variants.filtered(
                    lambda v: all(
                        val_id
                        in v.product_template_attribute_value_ids.mapped(
                            "product_attribute_value_id"
                        ).ids
                        for val_id in attrib_value_ids
                    )
                )

            # Price range filtering
            min_price = post.get("min_price")
            max_price = post.get("max_price")
            if min_price:
                try:
                    min_price = float(min_price)
                    variants = variants.filtered(lambda v: v.list_price >= min_price)
                except (ValueError, TypeError):
                    min_price = None
            if max_price:
                try:
                    max_price = float(max_price)
                    variants = variants.filtered(lambda v: v.list_price <= max_price)
                except (ValueError, TypeError):
                    max_price = None

            # Build attribute dictionary for filters
            attribute_dict = {}
            for variant in variants:
                for value in variant.product_template_attribute_value_ids.mapped(
                    "product_attribute_value_id"
                ):
                    attr_id = value.attribute_id.id
                    if attr_id not in attribute_dict:
                        attribute_dict[attr_id] = {
                            "attribute": value.attribute_id,
                            "values": {},
                        }
                    attribute_dict[attr_id]["values"][value.id] = {"value": value}

            attrib_values = list(attribute_dict.values())

            return request.render(
                "cr_parts_picker.products",
                {
                    "category": category,
                    "variants": variants,
                    "attrib_values": attrib_values,
                    "selected_attribs": selected_attribs,
                    "min_price": min_price,
                    "max_price": max_price,
                    "min_price_range": min_price_range,
                    "max_price_range": max_price_range,
                },
            )

    # @http.route(
    #     ["/parts-picker/add/<int:product_id>"], type="http", auth="public", website=True
    # )
    # def add_product_to_build(self, product_id, **post):
    #     _logger.info('>>>product_id : ',product_id)
    #     ProductVariant = request.env["product.product"].sudo().browse(product_id)
    #     if not ProductVariant.exists():
    #         return request.redirect("/parts-picker")
    #
    #     ProductTemplate = ProductVariant.product_tmpl_id
    #     # Get the first public category (leaf or normal)
    #     category = ProductTemplate.public_categ_ids[:1]
    #     if not category:
    #         return request.redirect("/parts-picker")
    #
    #     # Get top-level category
    #     top_category = category
    #     if top_category.is_optional:
    #         top_category = top_category
    #     else:
    #         if top_category.parent_id:
    #             top_category = top_category.parent_id
    #         else:
    #             top_category = top_category
    #
    #     category_id = str(top_category.id)
    #     allow_multiple = top_category.allow_multiple_products
    #     # ⚠️ Use the actual category (not walk to top)
    #     # category_id = str(category.id)
    #     # allow_multiple = category.allow_multiple_products
    #
    #     # Load build map from session
    #     build_map = request.session.get("pc_build_map", {})
    #     build_map = {str(k): v.copy() for k, v in build_map.items()}
    #
    #     # Remove from other categories
    #     for k in list(build_map.keys()):
    #         if k != category_id and product_id in build_map[k]:
    #             build_map[k].remove(product_id)
    #             if not build_map[k]:
    #                 del build_map[k]
    #
    #     # Add based on allow_multiple
    #     if allow_multiple:
    #         if category_id not in build_map:
    #             build_map[category_id] = []
    #         if product_id not in build_map[category_id]:
    #             build_map[category_id].append(product_id)
    #     else:
    #         build_map[category_id] = [product_id]
    #
    #     request.session["pc_build_map"] = build_map
    #     request.session.modified = True
    #
    #     return self.parts_picker(category_id=None)

    @http.route(
        ["/parts-picker/add/<int:product_id>"], type="http", auth="public", website=True
    )
    def add_product_to_build(self, product_id, **post):
        _logger.info(">>> Entering add_product_to_build()")
        _logger.info(f"Incoming product_id: {product_id}")
        _logger.info(f"POST data: {post}")

        ProductVariant = request.env["product.product"].sudo().browse(product_id)
        _logger.info(f"Browsed ProductVariant: {ProductVariant}")

        if not ProductVariant.exists():
            _logger.info("ProductVariant does not exist, redirecting to /parts-picker")
            return request.redirect("/parts-picker")

        ProductTemplate = ProductVariant.product_tmpl_id
        _logger.info(f"ProductTemplate ID: {ProductTemplate.id}")

        # Get the first public category
        category = ProductTemplate.public_categ_ids[:1]
        _logger.info(f"Initial category: {category}")

        if not category:
            _logger.info("No public category found -> redirecting")
            return request.redirect("/parts-picker")

        category = category[0]
        _logger.info(f"Using category record: {category.id} ({category.name})")

        # Determine top-level category logic
        top_category = category
        _logger.info(f"Initial top_category: {top_category.id}")

        if top_category.is_optional:
            _logger.info("Category is optional – staying with current category.")
            top_category = top_category
        else:
            # Walk up the category tree until reaching the root category
            while top_category.parent_id:
                _logger.info(
                    f"Category {top_category.id} ({top_category.name}) "
                    f"has parent -> moving to parent {top_category.parent_id.id} "
                    f"({top_category.parent_id.name})"
                )
                top_category = top_category.parent_id

            _logger.info(
                f"Reached root category: {top_category.id} ({top_category.name})"
            )

            # if top_category.parent_id:
            #     _logger.info(
            #         f"Category has parent -> moving to parent: {top_category.parent_id.id}"
            #     )
            #     top_category = top_category.parent_id
            # else:
            #     _logger.info("Category has no parent -> using itself.")

        _logger.info(f"Final top_category used: {top_category.id} ({top_category.name})")

        category_id = str(top_category.id)
        allow_multiple = top_category.allow_multiple_products
        _logger.info(f"category_id: {category_id}, allow_multiple: {allow_multiple}")

        # Load session map
        build_map = request.session.get("pc_build_map", {})
        _logger.info(f"Loaded build_map from session BEFORE: {build_map}")

        build_map = {str(k): v.copy() for k, v in build_map.items()}
        _logger.info(f"Normalized build_map: {build_map}")

        # Remove this product_id from all other categories
        _logger.info("Checking other categories to remove product if needed...")
        for k in list(build_map.keys()):
            _logger.info(f"Examining category key: {k} -> values: {build_map[k]}")
            if k != category_id and product_id in build_map[k]:
                _logger.info(f"Removing product_id {product_id} from category {k}")
                build_map[k].remove(product_id)
                if not build_map[k]:
                    _logger.info(f"Category {k} is now empty -> deleting key")
                    del build_map[k]

        # Add into correct category depending on allow_multiple
        _logger.info("Adding product to build_map...")
        if allow_multiple:
            if category_id not in build_map:
                _logger.info(f"Category {category_id} not in map -> creating new list")
                build_map[category_id] = []

            if product_id not in build_map[category_id]:
                _logger.info(f"Appending product_id {product_id} to category {category_id}")
                build_map[category_id].append(product_id)
            else:
                _logger.info(f"Product_id {product_id} already in category {category_id}")

        else:
            _logger.info(f"allow_multiple = False -> Overwriting category {category_id}")
            build_map[category_id] = [product_id]

        _logger.info(f"build_map AFTER updates: {build_map}")

        # Save session
        request.session["pc_build_map"] = build_map
        request.session.modified = True
        _logger.info("Session updated and marked modified.")

        _logger.info("Calling self.parts_picker() and returning result.")
        return self.parts_picker(category_id=None)

    @http.route(["/parts-picker"], type="http", auth="public", website=True)
    def parts_picker(self, category_id=None, **post):

        CategoryModel = request.env["product.public.category"].sudo()
        ProductModel = request.env["product.product"].sudo()

        build_map = request.session.get("pc_build_map", {})
        selected_products_by_category = {}

        base_total = 0.0
        currency = request.env.company.currency_id.symbol  # default fallback

        for cat_id_str, product_ids in build_map.items():
            cat_id = int(cat_id_str)
            category = CategoryModel.browse(cat_id)
            products = ProductModel.browse(product_ids)

            if category.exists() and products.exists():
                selected_products_by_category[cat_id] = {
                    "category": category,
                    "products": products,
                }

                for product in products:
                    base_total += product.list_price or 0.0
                    if product.cost_currency_id:
                        currency = product.cost_currency_id.symbol

        shipping_cost = 0.0
        grand_total = base_total + shipping_cost

        # Step 1: Fetch all top-level categories to display
        top_level_categories = CategoryModel.search(
            [("parent_id", "=", False), ("is_show_in_parts_picker", "=", True)],
            order="sequence ASC",
        )

        # Step 2: Split into normal and optional
        normal_categories = top_level_categories.filtered(lambda c: not c.is_optional)
        optional_parent_categories = top_level_categories.filtered(
            lambda c: c.is_optional
        )

        # Step 3: Fetch child categories for each optional parent
        optional_parent_children = {}
        for parent in optional_parent_categories:
            children = parent.child_id.filtered(lambda c: c.is_show_in_parts_picker)
            optional_parent_children[parent.id] = children

        # # Step 4: Ensure selected categories are always shown
        # all_category_ids = set(normal_categories.ids)
        # for cat_id in selected_products_by_category.keys():
        #     cat = CategoryModel.browse(cat_id)
        #     if cat.exists() and cat.is_show_in_parts_picker:
        #         all_category_ids.add(cat.id)
        #
        # categories = CategoryModel.browse(list(all_category_ids))

        # Step 4: Collect all category IDs to show
        optional_parent_children_ids = [
            child.id
            for children in optional_parent_children.values()
            for child in children
        ]

        all_category_ids = set(normal_categories.ids + optional_parent_children_ids)

        # Ensure any selected category is shown
        for cat_id in selected_products_by_category.keys():
            all_category_ids.add(cat_id)

        categories = CategoryModel.browse(list(all_category_ids))

        return request.render(
            "cr_parts_picker.categories",
            {
                "categories": normal_categories,
                "optional_parent_categories": optional_parent_categories,
                "optional_parent_children": optional_parent_children,
                "selected_products_by_category": selected_products_by_category,
                "base_total": base_total,
                "currency": currency,
                "shipping_cost": shipping_cost,
                "grand_total": grand_total,
            },
        )

    @http.route(
        ["/parts-picker/add-all-to-cart"],
        type="http",
        auth="public",
        website=True,
        csrf=False,
        methods=["POST"],
    )
    def add_all_to_cart(self, **post):
        build_map = request.session.get("pc_build_map", {})

        all_product_ids = []
        for product_ids in build_map.values():
            all_product_ids.extend(product_ids)

        if not all_product_ids:
            return request.redirect("/parts-picker")

        order = request.website.sale_get_order(force_create=True)

        ProductProduct = request.env["product.product"].sudo()
        products = ProductProduct.browse(all_product_ids)

        for product in products:
            if product.exists():
                order._cart_update(product_id=product.id, add_qty=1)

        # Clear the selection after adding to cart
        request.session["pc_build_map"] = {}
        request.session.modified = True

        return request.redirect("/shop/cart")

    @route(
        ["/parts-picker/remove/<int:product_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def remove_product_from_build(self, product_id, **post):
        # Product = request.env["product.template"].sudo().browse(product_id)
        Product = request.env["product.template"].sudo().search([('product_variant_id','=',product_id)])
        if not Product.exists():
            return request.redirect("/parts-picker")

        original_map = request.session.get("pc_build_map", {})
        build_map = deepcopy(original_map)  # <- Deep copy to ensure change detection

        removed = False
        for cid in list(build_map.keys()):
            if product_id in build_map[cid]:
                build_map[cid].remove(product_id)
                removed = True
                if not build_map[cid]:
                    del build_map[cid]

        if removed:
            request.session["pc_build_map"] = dict(
                build_map
            )  # Ensure it's a new object
            request.session.modified = True
        else:
            _logger.info("Product not found in any category")

        return request.redirect("/parts-picker")
