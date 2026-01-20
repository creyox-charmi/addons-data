# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import http
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
import werkzeug
import time
from copy import deepcopy

import logging

_logger = logging.getLogger(__name__)


class CrPartsPicker(WebsiteSale):

    # @route(['/parts-picker'], type='http', auth="public", website=True)
    # def parts_picker(self, category_id=None, **post):
    #     print(f"category_id received in parts_picker: {category_id}")
    #
    #     Category = request.env['product.public.category'].sudo()
    #     build_map = request.session.get('pc_build_map', {})
    #     selected_products_by_category = {}
    #
    #     for cat_id_str, product_ids in build_map.items():
    #         cat_id = int(cat_id_str)
    #         category = Category.browse(cat_id)
    #         products = request.env['product.template'].sudo().browse(product_ids)
    #         selected_products_by_category[category] = products
    #
    #     if category_id:
    #         current_category = Category.browse(int(category_id))
    #         if not current_category.exists():
    #             return request.redirect('/parts-picker')
    #
    #         if current_category.child_id:
    #             # Show child categories of current_category
    #             return request.render("cr_parts_picker.categories", {
    #                 'categories': current_category.child_id,
    #                 'selected_products_by_category': selected_products_by_category,
    #                 'parent_category': current_category,
    #             })
    #         else:
    #             # Show products in this category
    #             products = request.env['product.template'].sudo().search([
    #                 ('public_categ_ids', 'in', current_category.ids)
    #             ])
    #             return request.render("cr_parts_picker.products", {
    #                 'products': products,
    #                 'category': current_category,
    #                 'selected_products_by_category': selected_products_by_category,
    #             })
    #
    #     # Default: show top-level categories
    #     top_level = Category.search([('parent_id', '=', False)])
    #     top_with_children = top_level.filtered(lambda c: c.child_id)
    #
    #     return request.render("cr_parts_picker.categories", {
    #         'categories': top_with_children,
    #         'selected_products_by_category': selected_products_by_category,
    #     })

    # @route(['/parts-picker'], type='http', auth="public", website=True)
    # def parts_picker(self, category_id=None, **post):
    #     print("11")
    #     Category = request.env['product.public.category'].sudo()
    #
    #     build_map = request.session.get('pc_build_map', {})
    #     selected_products_by_category = {}
    #
    #     for cat_id_str, product_ids in build_map.items():
    #         cat_id = int(cat_id_str)
    #         category = Category.browse(cat_id)
    #         products = request.env['product.template'].sudo().browse(product_ids)
    #         selected_products_by_category[category] = products
    #
    #     top_level = Category.search([('parent_id', '=', False)])
    #     top_with_children = top_level.filtered(lambda c: c.child_id)
    #     all_category_ids = set(top_level.ids)
    #     all_category_ids.update(selected_products_by_category.keys())
    #
    #     categories = Category.browse(list(all_category_ids))
    #
    #     print('>>categories : ',categories)
    #     # print('selected_products_by_category : ',selected_products_by_category)
    #
    #     return request.render("cr_parts_picker.categories", {
    #         'categories': categories,
    #         'selected_products_by_category': selected_products_by_category,
    #     })

    # @route(['/parts-picker'], type='http', auth="public", website=True)
    # def parts_picker(self, category_id=None, **post):
    #     Category = request.env['product.public.category'].sudo()
    #     print('Category : ',Category)
    #
    #     build_map = request.session.get('pc_build_map', {})
    #     print('build_map : ', build_map)
    #     selected_products_by_category = {}
    #     print('selected_products_by_category : ', selected_products_by_category)
    #
    #     for cat_id_str, product_ids in build_map.items():
    #         cat_id = int(cat_id_str)
    #         category = Category.browse(cat_id)
    #         products = request.env['product.template'].sudo().browse(product_ids)
    #         selected_products_by_category[cat_id] = {
    #             'category': category,
    #             'products': products
    #         }
    #
    #     top_level = Category.search([('parent_id', '=', False)])
    #     print('top_level : ', top_level)
    #     all_category_ids = set(top_level.ids)
    #     print('all_category_ids : ', all_category_ids)
    #     all_category_ids.update(selected_products_by_category.keys())
    #     print('all_category_ids : ', all_category_ids)
    #
    #     categories = Category.browse(list(all_category_ids))
    #     print('categories : ', categories)
    #     print('selected_products_by_category : ', selected_products_by_category)
    #
    #     return request.render("cr_parts_picker.categories", {
    #         'categories': categories,
    #         'selected_products_by_category': selected_products_by_category,
    #     })

    # @http.route(['/parts-picker/category/<int:category_id>'], type='http', auth="public", website=True)
    # def parts_picker_category(self, category_id, **post):
    #     Category = request.env['product.public.category'].sudo()
    #     Product = request.env['product.template'].sudo()
    #
    #     category = Category.browse(category_id)
    #
    #     if category.child_id:
    #         # Render child category tree if current category has children
    #         print("sss")
    #         print('category : ',category)
    #         print('child_id : ', category.child_id)
    #         return request.render("cr_parts_picker.child_categories_tree", {
    #             'parent_category': category,
    #             'child_categories': category.child_id,
    #         })
    #     else:
    #         # Render products if it's a leaf category
    #         products = Product.search([('public_categ_ids', 'in', category.id)])
    #         return request.render("cr_parts_picker.products", {
    #             'category': category,
    #             'products': products,
    #         })

    # @http.route(['/parts-picker/category/<int:category_id>'], type='http', auth="public", website=True)
    # def parts_picker_category(self, category_id, **post):
    #     Category = request.env['product.public.category'].sudo()
    #     Product = request.env['product.template'].sudo()
    #
    #     category = Category.browse(category_id)
    #     domain = [('public_categ_ids', 'in', category.id)]
    #
    #     # Read GET params from request
    #     selected_attribs = request.httprequest.args.getlist('attrib')
    #     attrib_value_ids = []
    #
    #     for attrib_pair in selected_attribs:
    #         try:
    #             _, value_id = attrib_pair.split('-')
    #             attrib_value_ids.append(int(value_id))
    #         except Exception:
    #             continue
    #
    #     if attrib_value_ids:
    #         domain += [('product_variant_ids.product_template_attribute_value_ids', 'in', attrib_value_ids)]
    #
    #     products = Product.search(domain)
    #
    #     # Build attribute sidebar using attribute_line_ids
    #     attribute_dict = {}
    #     product_templates = Product.search([('public_categ_ids', 'in', category.id)])
    #     for template in product_templates:
    #         for line in template.attribute_line_ids:
    #             attr = line.attribute_id
    #             if attr.id not in attribute_dict:
    #                 attribute_dict[attr.id] = {
    #                     'attribute': attr,
    #                     'values': {}
    #                 }
    #             for val in line.value_ids:
    #                 if val.id not in attribute_dict[attr.id]['values']:
    #                     attribute_dict[attr.id]['values'][val.id] = {'value': val}
    #
    #     attrib_values = list(attribute_dict.values())
    #
    #     return request.render("cr_parts_picker.products", {
    #         'category': category,
    #         'products': products,
    #         'attrib_values': attrib_values,
    #         'selected_attribs': selected_attribs,
    #     })

    # @http.route(['/parts-picker/category/<int:category_id>'], type='http', auth="public", website=True)
    # def parts_picker_category(self, category_id, **post):
    #     Category = request.env['product.public.category'].sudo()
    #     Product = request.env['product.template'].sudo()
    #
    #     category = Category.browse(category_id)
    #
    #     # Abort if this category should not show in parts picker
    #     if not category.is_show_in_parts_picker:
    #         return request.render("website.404")  # or redirect to /parts-picker/home
    #
    #     # Get direct products for this category
    #     direct_products = Product.search([
    #         ('public_categ_ids', 'in', category.id)
    #     ])
    #
    #     # Get subcategories that are allowed in parts picker
    #     subcategories = Category.search([
    #         ('parent_id', '=', category.id),
    #         ('is_show_in_parts_picker', '=', True)
    #     ])
    #
    #     # Prepare subcategory -> products mapping
    #     subcategory_products = {}
    #     for subcat in subcategories:
    #         products = Product.search([
    #             ('public_categ_ids', 'in', subcat.id)
    #         ])
    #         if products:
    #             subcategory_products[subcat] = products
    #
    #     # Attribute filter parsing
    #     selected_attribs = request.httprequest.args.getlist('attrib')
    #     attrib_value_ids = []
    #     for attrib_pair in selected_attribs:
    #         try:
    #             _, value_id = attrib_pair.split('-')
    #             attrib_value_ids.append(int(value_id))
    #         except Exception:
    #             continue
    #
    # if attrib_value_ids:
    #     # Filter direct products
    #     direct_products = direct_products.filtered(
    #         lambda p: any(val.id in attrib_value_ids for val in
    #                       p.product_variant_ids.mapped('product_template_attribute_value_ids').mapped('value_id'))
    #     )
    #         # Filter each subcategory's products
    #         for subcat in list(subcategory_products.keys()):
    #             products = subcategory_products[subcat]
    #             filtered = products.filtered(
    #                 lambda p: any(val.id in attrib_value_ids for val in
    #                               p.product_variant_ids.mapped('product_template_attribute_value_ids').mapped(
    #                                   'value_id'))
    #             )
    #             subcategory_products[subcat] = filtered
    #
    #     # Build sidebar attributes from all visible products
    #     all_products = direct_products + sum(subcategory_products.values(), request.env['product.template'])
    #     attribute_dict = {}
    #     for template in all_products:
    #         for line in template.attribute_line_ids:
    #             attr = line.attribute_id
    #             if attr.id not in attribute_dict:
    #                 attribute_dict[attr.id] = {
    #                     'attribute': attr,
    #                     'values': {}
    #                 }
    #             for val in line.value_ids:
    #                 if val.id not in attribute_dict[attr.id]['values']:
    #                     attribute_dict[attr.id]['values'][val.id] = {'value': val}
    #
    #     attrib_values = list(attribute_dict.values())
    #
    #     return request.render("cr_parts_picker.products", {
    #         'category': category,
    #         'direct_products': direct_products,
    #         'subcategory_products': subcategory_products,
    #         'attrib_values': attrib_values,
    #         'selected_attribs': selected_attribs,
    #     })

    # @http.route(['/parts-picker/category/<int:category_id>'], type='http', auth="public", website=True)
    # def parts_picker_category(self, category_id, **post):
    #     Category = request.env['product.public.category'].sudo()
    #     Product = request.env['product.template'].sudo()
    #
    #     category = Category.browse(category_id)
    #
    #     if category.child_id:
    #         # Render child category tree if current category has children
    #         print("sss")
    #         print('category : ', category)
    #         print('child_id : ', category.child_id)
    #         return request.render("cr_parts_picker.child_categories_tree", {
    #             'parent_category': category,
    #             'child_categories': category.child_id,
    #         })
    #     else:
    #         # Render products if it's a leaf category
    #         products = Product.search([('public_categ_ids', 'in', category.id)])
    #         return request.render("cr_parts_picker.products", {
    #             'category': category,
    #             'products': products,
    #         })

    # product category with product template
    # @http.route(['/parts-picker/category/<int:category_id>'], type='http', auth="public", website=True)
    # def parts_picker_category(self, category_id, **post):
    #     Category = request.env['product.public.category'].sudo()
    #     Product = request.env['product.template'].sudo()
    #
    #     category = Category.browse(category_id)
    #
    #     # If category doesn't exist or not marked to show, show 404
    #     # if not category.exists() or not category.is_show_in_parts_picker:
    #     #     return request.render("website.404")
    #
    #     # Filter child categories with is_show_in_parts_picker = True
    #     visible_children = category.child_id.filtered(lambda c: c.is_show_in_parts_picker)
    #
    #     if visible_children:
    #         # Show child category tree
    #         return request.render("cr_parts_picker.child_categories_tree", {
    #             'parent_category': category,
    #             'child_categories': visible_children,
    #         })
    #
    #     else:
    #         # Get products for this leaf category
    #         products = Product.search([('public_categ_ids', 'in', category.id)])
    #
    #         # Parse selected attributes like ['1-5', '2-9']
    #         selected_attribs = post.getlist('attrib') if hasattr(post, 'getlist') else post.get('attrib', [])
    #         if isinstance(selected_attribs, str):
    #             selected_attribs = [selected_attribs]
    #
    #         attrib_value_ids = []
    #         for attrib_pair in selected_attribs:
    #             try:
    #                 _, value_id = attrib_pair.split('-')
    #                 attrib_value_ids.append(int(value_id))
    #             except Exception:
    #                 continue
    #
    #         if attrib_value_ids:
    #             products = products.filtered(
    #                 lambda p: any(
    #                     val.product_attribute_value_id.id in attrib_value_ids
    #                     for v in p.product_variant_ids
    #                     for val in v.product_template_attribute_value_ids
    #                 )
    #             )
    #
    #         attribute_dict = {}
    #         for product in products:
    #             for variant in product.product_variant_ids:
    #                 for value in variant.product_template_attribute_value_ids.mapped('product_attribute_value_id'):
    #                     attr_id = value.attribute_id.id
    #                     if attr_id not in attribute_dict:
    #                         attribute_dict[attr_id] = {
    #                             'attribute': value.attribute_id,
    #                             'values': {}
    #                         }
    #                     attribute_dict[attr_id]['values'][value.id] = {'value': value}
    #
    #         attrib_values = list(attribute_dict.values())
    #
    #         return request.render("cr_parts_picker.products", {
    #             'category': category,
    #             'products': products,
    #             'attrib_values': attrib_values,
    #             'selected_attribs': selected_attribs,
    #         })

    @http.route(['/parts-picker/category/<int:category_id>'], type='http', auth="public", website=True)
    def parts_picker_category(self, category_id, **post):
        Category = request.env['product.public.category'].sudo()
        ProductVariant = request.env['product.product'].sudo()

        category = Category.browse(category_id)

        # Filter child categories with is_show_in_parts_picker = True
        visible_children = category.child_id.filtered(lambda c: c.is_show_in_parts_picker)

        if visible_children:
            return request.render("cr_parts_picker.child_categories_tree", {
                'parent_category': category,
                'child_categories': visible_children,
            })

        else:
            # Get variants whose template has this category
            variants = ProductVariant.search([
                ('product_tmpl_id.public_categ_ids', 'in', category.id)
            ])

            # Parse selected attributes like ['1-5', '2-9']
            selected_attribs = post.getlist('attrib') if hasattr(post, 'getlist') else post.get('attrib', [])
            if isinstance(selected_attribs, str):
                selected_attribs = [selected_attribs]

            attrib_value_ids = []
            for attrib_pair in selected_attribs:
                try:
                    _, value_id = attrib_pair.split('-')
                    attrib_value_ids.append(int(value_id))
                except Exception:
                    continue

            if attrib_value_ids:
                # Keep variants that have all selected attribute values
                variants = variants.filtered(
                    lambda v: all(
                        val_id in v.product_template_attribute_value_ids.mapped('product_attribute_value_id').ids
                        for val_id in attrib_value_ids
                    )
                )

            # Build attribute dictionary for filters
            attribute_dict = {}
            for variant in variants:
                for value in variant.product_template_attribute_value_ids.mapped('product_attribute_value_id'):
                    attr_id = value.attribute_id.id
                    if attr_id not in attribute_dict:
                        attribute_dict[attr_id] = {
                            'attribute': value.attribute_id,
                            'values': {}
                        }
                    attribute_dict[attr_id]['values'][value.id] = {'value': value}

            attrib_values = list(attribute_dict.values())
            print('variants : ', variants)
            return request.render("cr_parts_picker.products", {
                'category': category,
                'variants': variants,  # Note: renamed key from 'products' to 'variants'
                'attrib_values': attrib_values,
                'selected_attribs': selected_attribs,
            })

    # @route(['/parts-picker/add/<int:product_id>'], type='http', auth="public", website=True)
    # def add_product_to_build(self, product_id, **post):
    #     Product = request.env['product.template'].sudo().browse(product_id)
    #     if not Product.exists():
    #         return request.redirect('/parts-picker')
    #
    #     category = Product.public_categ_ids[:1]
    #     if not category:
    #         return request.redirect('/parts-picker')
    #
    #     parent_category = category
    #     while parent_category.parent_id:
    #         parent_category = parent_category.parent_id
    #     top_level_id = parent_category.id
    #
    #     print(f"Initial Category: {category}")
    #     print(f"Top-level Category ID: {top_level_id}")
    #
    #     # ✅ Ensure consistent key types
    #     build_map = request.session.get('pc_build_map', {})
    #     build_map = {str(k): v for k, v in build_map.items()}
    #
    #     print("Before adding:", build_map)
    #     product_list = build_map.get(str(top_level_id), [])
    #
    #     # ✅ Optional: Remove product from any other category
    #     for cid in list(build_map.keys()):
    #         if product_id in build_map[cid] and cid != str(top_level_id):
    #             build_map[cid].remove(product_id)
    #             if not build_map[cid]:
    #                 del build_map[cid]
    #
    #     if product_id not in product_list:
    #         product_list.append(product_id)
    #         build_map[str(top_level_id)] = product_list
    #
    #     print("After adding:", build_map)
    #
    #     # ✅ Persist session properly
    #     request.session['pc_build_map'] = build_map
    #     request.session.modified = True
    #
    #     return request.redirect('/parts-picker')

    @route(['/parts-picker/add/<int:product_id>'], type='http', auth="public", website=True)
    def add_product_to_build(self, product_id, **post):
        # Product = request.env['product.template'].sudo().browse(product_id)
        # if not Product.exists():
        #     return request.redirect('/parts-picker')
        #
        # # 🧠 Get first public category
        # category = Product.public_categ_ids[:1]

        ProductVariant = request.env['product.product'].sudo().browse(product_id)
        if not ProductVariant.exists():
            return request.redirect('/parts-picker')

        ProductTemplate = ProductVariant.product_tmpl_id
        category = ProductTemplate.public_categ_ids[:1]
        if not category:
            return request.redirect('/parts-picker')

        # 🔍 Get top-level category
        top_category = category
        while top_category.parent_id:
            top_category = top_category.parent_id

        category_id = str(top_category.id)
        allow_multiple = top_category.allow_multiple_products

        # Load build map from session
        build_map = request.session.get('pc_build_map', {})
        build_map = {str(k): v.copy() for k, v in build_map.items()}  # ensure we don’t mutate shared references

        print("Before adding:", build_map)

        # 🧹 Remove product from all other categories except this one
        for k in list(build_map.keys()):
            if k != category_id and product_id in build_map[k]:
                build_map[k].remove(product_id)
                if not build_map[k]:
                    del build_map[k]

        # ✅ Handle multiple or single selection
        if allow_multiple:
            if category_id not in build_map:
                build_map[category_id] = []
            if product_id not in build_map[category_id]:
                build_map[category_id].append(product_id)
        else:
            build_map[category_id] = [product_id]  # Replace existing

        print("After adding:", build_map)

        # Save to session
        request.session['pc_build_map'] = build_map
        request.session.modified = True

        return self.parts_picker(category_id=None)

    # @route(['/parts-picker'], type='http', auth="public", website=True)
    # def parts_picker(self, category_id=None, **post):
    #     print("in /parts-picker")
    #     print("Session ID:", request.session.sid)
    #     print("Session keys:", list(request.session.keys()))
    #     print("Full session data:", dict(request.session))
    #
    #     CategoryModel = request.env['product.public.category'].sudo()
    #     ProductModel = request.env['product.template'].sudo()
    #     print("Session ID on parts-picker:", request.session.sid)
    #
    #     build_map = request.session.get('pc_build_map', {})
    #     print('build_map : ',build_map)
    #     selected_products_by_category = {}
    #
    #     for cat_id_str, product_ids in build_map.items():
    #         cat_id = int(cat_id_str)
    #         category = CategoryModel.browse(cat_id)
    #         products = ProductModel.browse(product_ids)
    #
    #         print(f'Category ID: {cat_id}, Category: {category}, Exists: {category.exists()}')
    #         print(f'Products: {products}, Exists: {products.exists()}')
    #
    #         if category.exists() and products.exists():
    #             selected_products_by_category[cat_id] = {
    #                 'category': category,
    #                 'products': products
    #             }
    #
    #     top_level = CategoryModel.search([('parent_id', '=', False)])
    #     all_category_ids = set(top_level.ids)
    #     all_category_ids.update(selected_products_by_category.keys())
    #     categories = CategoryModel.browse(list(all_category_ids))
    #     print('categories : ', categories)
    #     print('selected_products_by_category : ',selected_products_by_category)
    #     return request.render("cr_parts_picker.categories", {
    #         'categories': categories,
    #         'selected_products_by_category': selected_products_by_category,
    #     })

    # with shipping
    # @route(['/parts-picker'], type='http', auth="public", website=True)
    # def parts_picker(self, category_id=None, **post):
    #     print("in /parts-picker")
    #     print("Session ID:", request.session.sid)
    #     print("Session keys:", list(request.session.keys()))
    #     print("Full session data:", dict(request.session))
    #
    #     CategoryModel = request.env['product.public.category'].sudo()
    #     ProductModel = request.env['product.template'].sudo()
    #     print("Session ID on parts-picker:", request.session.sid)
    #
    #     build_map = request.session.get('pc_build_map', {})
    #     print('build_map : ', build_map)
    #     selected_products_by_category = {}
    #
    #     base_total = 0.0  # Initialize base total
    #
    #     for cat_id_str, product_ids in build_map.items():
    #         cat_id = int(cat_id_str)
    #         category = CategoryModel.browse(cat_id)
    #         products = ProductModel.browse(product_ids)
    #
    #         print(f'Category ID: {cat_id}, Category: {category}, Exists: {category.exists()}')
    #         print(f'Products: {products}, Exists: {products.exists()}')
    #
    #         if category.exists() and products.exists():
    #             selected_products_by_category[cat_id] = {
    #                 'category': category,
    #                 'products': products
    #             }
    #
    #             # Accumulate total base price
    #             for product in products:
    #                 base_total += product.list_price or 0.0
    #
    #     # Define static shipping cost (can be made dynamic)
    #     shipping_cost = 9.99 if base_total > 0 else 0.0
    #     grand_total = base_total + shipping_cost
    #
    #     # Load relevant categories (top-level and those with selected products)
    #     top_level = CategoryModel.search([('parent_id', '=', False)])
    #     all_category_ids = set(top_level.ids)
    #     all_category_ids.update(selected_products_by_category.keys())
    #     categories = CategoryModel.browse(list(all_category_ids))
    #
    #     print('categories : ', categories)
    #     print('selected_products_by_category : ', selected_products_by_category)
    #     print(f'base_total: {base_total}, shipping_cost: {shipping_cost}, grand_total: {grand_total}')
    #
    #     return request.render("cr_parts_picker.categories", {
    #         'categories': categories,
    #         'selected_products_by_category': selected_products_by_category,
    #         'base_total': base_total,
    #         'shipping_cost': shipping_cost,
    #         'grand_total': grand_total,
    #     })

    @http.route(['/parts-picker'], type='http', auth="public", website=True)
    def parts_picker(self, category_id=None, **post):
        print("in /parts-picker")
        print("Session ID:", request.session.sid)
        print("Session keys:", list(request.session.keys()))
        print("Full session data:", dict(request.session))

        CategoryModel = request.env['product.public.category'].sudo()
        # ProductModel = request.env['product.template'].sudo()
        ProductModel = request.env['product.product'].sudo()

        print("Session ID on parts-picker:", request.session.sid)

        build_map = request.session.get('pc_build_map', {})
        print('build_map : ', build_map)
        selected_products_by_category = {}

        base_total = 0.0  # Initialize base total

        for cat_id_str, product_ids in build_map.items():
            cat_id = int(cat_id_str)
            category = CategoryModel.browse(cat_id)
            products = ProductModel.browse(product_ids)

            print(f'Category ID: {cat_id}, Category: {category}, Exists: {category.exists()}')
            print(f'Products: {products}, Exists: {products.exists()}')

            if category.exists() and products.exists():
                selected_products_by_category[cat_id] = {
                    'category': category,
                    'products': products
                }

                for product in products:
                    base_total += product.list_price or 0.0

        shipping_cost = 0.0 if base_total > 0 else 0.0
        grand_total = base_total + shipping_cost

        # ✅ Only include top-level categories where is_show_in_parts_picker is True
        top_level = CategoryModel.search([
            ('parent_id', '=', False),
            ('is_show_in_parts_picker', '=', True)
        ])

        # ✅ Add selected categories (in case some are not top-level, check is_show_in_parts_picker)
        all_category_ids = set(top_level.ids)
        for cat_id in selected_products_by_category.keys():
            cat = CategoryModel.browse(cat_id)
            if cat.exists() and cat.is_show_in_parts_picker:
                all_category_ids.add(cat.id)

        categories = CategoryModel.browse(list(all_category_ids))

        print('categories : ', categories)
        print('selected_products_by_category : ', selected_products_by_category)
        print(f'base_total: {base_total}, shipping_cost: {shipping_cost}, grand_total: {grand_total}')

        return request.render("cr_parts_picker.categories", {
            'categories': categories,
            'selected_products_by_category': selected_products_by_category,
            'base_total': base_total,
            'shipping_cost': shipping_cost,
            'grand_total': grand_total,
        })

    # @route(['/parts-picker/remove/<int:product_id>'], type='http', auth="public", website=True)
    # def remove_product_from_build(self, product_id, **post):
    #     Product = request.env['product.template'].sudo().browse(product_id)
    #     if not Product.exists():
    #         return request.redirect('/parts-picker')
    #
    #     category = Product.public_categ_ids[:1]
    #     if not category:
    #         return request.redirect('/parts-picker')
    #
    #     parent_category = category
    #     while parent_category.parent_id:
    #         parent_category = parent_category.parent_id
    #
    #     cat_id = parent_category.id
    #     build_map = request.session.get('pc_build_map', {})
    #     product_list = build_map.get(str(cat_id), [])
    #
    #     if product_id in product_list:
    #         product_list.remove(product_id)
    #         if product_list:
    #             build_map[str(cat_id)] = product_list
    #         else:
    #             build_map.pop(str(cat_id))
    #         request.session['pc_build_map'] = build_map
    #
    #     return request.redirect('/parts-picker')

    # product template
    # @http.route(['/parts-picker/add-all-to-cart'], type='http', auth='public', website=True, csrf=False,
    #             methods=['POST'])
    # def add_all_to_cart(self, **post):
    #     build_map = request.session.get('pc_build_map', {})
    #
    #     all_product_ids = []
    #     for product_ids in build_map.values():
    #         all_product_ids.extend(product_ids)
    #
    #     if not all_product_ids:
    #         return request.redirect('/parts-picker')
    #
    #     order = request.website.sale_get_order(force_create=True)
    #
    #     for pid in all_product_ids:
    #         product = request.env['product.product'].sudo().search([('product_tmpl_id', '=', pid)], limit=1)
    #         if product:
    #             order._cart_update(product_id=product.id, add_qty=1)
    #
    #     # Clear the selection after adding to cart
    #     request.session['pc_build_map'] = {}
    #
    #     return request.redirect('/shop/cart')

    @http.route(
        ['/parts-picker/add-all-to-cart'],
        type='http',
        auth='public',
        website=True,
        csrf=False,
        methods=['POST']
    )
    def add_all_to_cart(self, **post):
        build_map = request.session.get('pc_build_map', {})

        all_product_ids = []
        for product_ids in build_map.values():
            all_product_ids.extend(product_ids)

        if not all_product_ids:
            return request.redirect('/parts-picker')

        order = request.website.sale_get_order(force_create=True)

        ProductProduct = request.env['product.product'].sudo()
        products = ProductProduct.browse(all_product_ids)

        for product in products:
            if product.exists():
                order._cart_update(product_id=product.id, add_qty=1)

        # Clear the selection after adding to cart
        request.session['pc_build_map'] = {}
        request.session.modified = True

        return request.redirect('/shop/cart')

    @route(['/parts-picker/remove/<int:product_id>'], type='http', auth="public", website=True)
    def remove_product_from_build(self, product_id, **post):
        _logger.info(f"Trying to remove product_id: {product_id}")

        Product = request.env['product.template'].sudo().browse(product_id)
        if not Product.exists():
            _logger.warning("Product does not exist")
            return request.redirect('/parts-picker')

        original_map = request.session.get('pc_build_map', {})
        build_map = deepcopy(original_map)  # <- Deep copy to ensure change detection

        removed = False
        for cid in list(build_map.keys()):
            if product_id in build_map[cid]:
                build_map[cid].remove(product_id)
                removed = True
                if not build_map[cid]:
                    del build_map[cid]

        if removed:
            request.session['pc_build_map'] = dict(build_map)  # Ensure it's a new object
            request.session.modified = True
            _logger.info(f"Updated build_map: {build_map}")
        else:
            _logger.info("Product not found in any category")

        return request.redirect('/parts-picker')


    # @route(['/parts-picker/add/<int:product_id>'], type='http', auth="public", website=True)
    #
    #
    # def add_product_to_build(self, product_id, **post):
    #     Product = request.env['product.template'].sudo().browse(product_id)
    #     if not Product.exists():
    #         return request.redirect('/parts-picker')
    #
    #     # 🧠 Get first public category
    #     category = Product.public_categ_ids[:1]
    #     if not category:
    #         return request.redirect('/parts-picker')
    #
    #     # 🔍 Get top-level category
    #     top_category = category
    #     while top_category.parent_id:
    #         top_category = top_category.parent_id
    #
    #     category_id = str(top_category.id)
    #     allow_multiple = top_category.allow_multiple_products
    #
    #     # Load build map from session
    #     build_map = request.session.get('pc_build_map', {})
    #     build_map = {str(k): v.copy() for k, v in build_map.items()}  # ensure we don’t mutate shared references
    #
    #     print("Before adding:", build_map)
    #
    #     # 🧹 Remove product from all other categories except this one
    #     for k in list(build_map.keys()):
    #         if k != category_id and product_id in build_map[k]:
    #             build_map[k].remove(product_id)
    #             if not build_map[k]:
    #                 del build_map[k]
    #
    #     # ✅ Handle multiple or single selection
    #     if allow_multiple:
    #         if category_id not in build_map:
    #             build_map[category_id] = []
    #         if product_id not in build_map[category_id]:
    #             build_map[category_id].append(product_id)
    #     else:
    #         build_map[category_id] = [product_id]  # Replace existing
    #
    #     print("After adding:", build_map)
    #
    #     # Save to session
    #     request.session['pc_build_map'] = build_map
    #     request.session.modified = True
    #
    #     return self.parts_picker(category_id=None)
    #
    # @http.route(['/parts-picker'], type='http', auth="public", website=True)
    # def parts_picker(self, category_id=None, **post):
    #     print("in /parts-picker")
    #     print("Session ID:", request.session.sid)
    #     print("Session keys:", list(request.session.keys()))
    #     print("Full session data:", dict(request.session))
    #
    #     CategoryModel = request.env['product.public.category'].sudo()
    #     ProductModel = request.env['product.template'].sudo()
    #     print("Session ID on parts-picker:", request.session.sid)
    #
    #     build_map = request.session.get('pc_build_map', {})
    #     print('build_map : ', build_map)
    #     selected_products_by_category = {}
    #
    #     base_total = 0.0  # Initialize base total
    #
    #     for cat_id_str, product_ids in build_map.items():
    #         cat_id = int(cat_id_str)
    #         category = CategoryModel.browse(cat_id)
    #         products = ProductModel.browse(product_ids)
    #
    #         print(f'Category ID: {cat_id}, Category: {category}, Exists: {category.exists()}')
    #         print(f'Products: {products}, Exists: {products.exists()}')
    #
    #         if category.exists() and products.exists():
    #             selected_products_by_category[cat_id] = {
    #                 'category': category,
    #                 'products': products
    #             }
    #
    #             for product in products:
    #                 base_total += product.list_price or 0.0
    #
    #     shipping_cost = 0.0 if base_total > 0 else 0.0
    #     grand_total = base_total + shipping_cost
    #
    #     # ✅ Only include top-level categories where is_show_in_parts_picker is True
    #     top_level = CategoryModel.search([
    #         ('parent_id', '=', False),
    #         ('is_show_in_parts_picker', '=', True)
    #     ])
    #
    #     # ✅ Add selected categories (in case some are not top-level, check is_show_in_parts_picker)
    #     all_category_ids = set(top_level.ids)
    #     for cat_id in selected_products_by_category.keys():
    #         cat = CategoryModel.browse(cat_id)
    #         if cat.exists() and cat.is_show_in_parts_picker:
    #             all_category_ids.add(cat.id)
    #
    #     categories = CategoryModel.browse(list(all_category_ids))
    #
    #     print('categories : ', categories)
    #     print('selected_products_by_category : ', selected_products_by_category)
    #     print(f'base_total: {base_total}, shipping_cost: {shipping_cost}, grand_total: {grand_total}')
    #
    #     return request.render("cr_parts_picker.categories", {
    #         'categories': categories,
    #         'selected_products_by_category': selected_products_by_category,
    #         'base_total': base_total,
    #         'shipping_cost': shipping_cost,
    #         'grand_total': grand_total,
    #     })
