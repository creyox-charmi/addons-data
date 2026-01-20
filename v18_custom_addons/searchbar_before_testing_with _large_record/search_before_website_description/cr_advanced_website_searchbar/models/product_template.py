# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _search_get_detail(self, website, order, options):
        ref = super()._search_get_detail(website, order, options)
        ref.clear()

        fields = {
            "name": self.env.user.company_id.cr_name,
            "default_code": self.env.user.company_id.internal_reference,
            "website_description": self.env.user.company_id.description,
            "description_ecommerce": self.env.user.company_id.website_description,
            "product_tag_ids.name": self.env.user.company_id.tags,
            "product_variant_ids.name": self.env.user.company_id.attributes,
        }

        # Sort the dictionary items by value (percentage) in ascending order
        sorted_fields = sorted(fields.items(), key=lambda x: x[1], reverse=True)

        # Print the sorted list of tuples (field_name, percentage)
        sorted_field_names = [key for key, _ in sorted_fields]
        search_fields = sorted_field_names
        search_fields.append('product_variant_ids.default_code')

        with_image = options['displayImage']
        with_description = options['displayDescription']
        with_category = options['displayExtraLink']
        with_price = options['displayDetail']
        domains = [website.sale_product_domain()]
        category = options.get('category')
        tags = options.get('tags')
        min_price = options.get('min_price')
        max_price = options.get('max_price')
        attrib_values = options.get('attrib_values')
        if category:
            domains.append([('public_categ_ids', 'child_of', self.env['ir.http']._unslug(category)[1])])
        if tags:
            if isinstance(tags, str):
                tags = tags.split(',')
            domains.append([('product_variant_ids.all_product_tag_ids', 'in', tags)])
        if min_price:
            domains.append([('list_price', '>=', min_price)])
        if max_price:
            domains.append([('list_price', '<=', max_price)])
        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        fetch_fields = ['id', 'name', 'website_url']
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'default_code': {'name': 'default_code', 'type': 'text', 'match': True},
            'product_variant_ids.default_code': {'name': 'product_variant_ids.default_code', 'type': 'text',
                                                 'match': True},
            'website_url': {'name': 'website_url', 'type': 'text', 'truncate': False},
        }
        if with_image:
            mapping['image_url'] = {'name': 'image_url', 'type': 'html'}
        if with_description:
            fetch_fields.append('website_description')
            fetch_fields.append('description_ecommerce')
            mapping['website_description'] = {'name': 'website_description', 'type': 'html', 'match': True}
            mapping['description_ecommerce'] = {'name': 'description_ecommerce', 'type': 'html', 'match': True}
        if with_price:
            mapping['detail'] = {'name': 'price', 'type': 'html', 'display_currency': options['display_currency']}
            mapping['detail_strike'] = {'name': 'list_price', 'type': 'html',
                                        'display_currency': options['display_currency']}
        if with_category:
            mapping['extra_link'] = {'name': 'category', 'type': 'html'}
        result = {
            'model': 'product.template',
            'base_domain': domains,
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-shopping-cart',
        }
        ref.update(result)
        print('ref : ',ref)
        return ref

