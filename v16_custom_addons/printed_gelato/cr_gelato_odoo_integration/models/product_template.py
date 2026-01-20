from odoo import Command, _, api, fields, models
import requests
from odoo.exceptions import UserError
import logging
import base64

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cr_template_ref = fields.Char(string="Template Reference from Gelato")
    cr_product_uid = fields.Char(
        string="Product UID of Gelato",
        compute='_compute_gelato_product_uid',
        inverse='_inverse_gelato_product_uid',
        readonly=True,
    )
    cr_image_ids = fields.One2many(
        string="Print Images",
        comodel_name='cr.product.doc',
        inverse_name='res_id',
        domain=[('is_gelato', '=', True)],
        readonly=True,
    )
    cr_missing_images = fields.Boolean(string="Missing Print Images")
    cr_product_doc_ids = fields.One2many(
        string="Docs",
        comodel_name='cr.product.doc',
        inverse_name='res_id',
        domain=lambda self: [('res_model', '=', self._name)])
    product_doc_count = fields.Integer(
        string="Docs Count", compute='_compute_product_doc_count')

    def _compute_product_doc_count(self):
        for data in self:
            data.product_doc_count = data.env['cr.product.doc'].search_count([
                '|',
                    '&', ('res_model', '=', 'product.template'), ('res_id', '=', data.id),
                    '&',
                        ('res_model', '=', 'product.product'),
                        ('res_id', 'in', data.product_variant_ids.ids),
            ])

    def action_open_cr_docs(self):
        self.ensure_one()
        return {
            'name': _('Docs'),
            'type': 'ir.actions.act_window',
            'res_model': 'cr.product.doc',
            'view_mode': 'tree,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_company_id': self.company_id.id,
            },
            'domain': [
                '|',
                '&', ('res_model', '=', 'product.template'), ('res_id', '=', self.id),
                '&',
                ('res_model', '=', 'product.product'),
                ('res_id', 'in', self.product_variant_ids.ids),
            ],
            'target': 'current',
        }

    @api.depends('product_variant_ids.cr_product_uid')
    def _compute_gelato_product_uid(self):
        self._compute_cr_template_field_from_variant_field('cr_product_uid')

    def _compute_cr_template_field_from_variant_field(self, fname, default=False):
        for data in self:
            var_count = len(data.product_variant_ids)
            if var_count == 1:
                data[fname] = data.product_variant_ids[fname]
            elif var_count == 0 and self.env.context.get("active_test", True):
                # If the product has no active variants, retry without the active_test
                temp_ref = data.with_context(active_test=False)
                temp_ref._compute_cr_template_field_from_variant_field(fname, default=default)
            else:
                data[fname] = default

    def _inverse_gelato_product_uid(self):
        self._set_product_variant_field('cr_product_uid')

    def action_sync_gelato_template_info(self):
        try:
            endpoint = f'templates/{self.cr_template_ref}'
            _logger.info(f"key >>>>>> {self.env.company.sudo().api_key_for_gelato} ")
            key = self.env.company.sudo().api_key_for_gelato
            template_data = self.gelato_api_request(endpoint, 'ecommerce', key, 'v1', 'GET')
            _logger.info(f"==========================================")
            _logger.info(f"template_data >>>>>> {template_data} ")
            _logger.info(f"==========================================")
        except UserError as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': _("Could not synchronize with Gelato"),
                    'message': str(e),
                    'sticky': True,
                }
            }

        self._create_attributes_for_product(template_data)
        self._create_print_images_for_product(template_data)

        product = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        for data in product:
            _logger.info(f"==============99999==================")
            _logger.info(f"data: {data}")
            _logger.info(f"================================")
            if data.cr_product_uid:
                data.list_price = self.apply_price(data.cr_product_uid)

        # Display a toaster notification to the user if all went well.
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Successfully synchronized with Gelato"),
                'message': _("Missing product variants and images have been successfully created."),
                'sticky': False,
                'next': {
                    'type': 'ir.actions.client',
                    'tag': 'soft_reload'
                }
            }
        }

    def gelato_api_request(self, endpoint, subdomain, api_key, version, payload=None, method='GET'):
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        try:
            _logger.info(f"Sending {method} request to {endpoint}")

            url = f'https://{subdomain}.gelatoapis.com/{version}/{endpoint}'
            headers = {
                'X-API-KEY': api_key or None
            }
            if method == 'GET':
                _logger.info(f">>>>>>> IN GET")
                response = requests.get(url=url, params=payload, headers=headers, timeout=10)
            else:
                _logger.info(f">>>>>>> IN POST")
                response = requests.post(url=url, json=payload, headers=headers, timeout=10)
            response_content = response.json()

            _logger.info(f"Response Status: {response.status_code} and response : {response_content}")
            response.raise_for_status()  # Raise exception for HTTP errors

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            _logger.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            _logger.error(f"Request error occurred: {req_err}")
        except Exception as err:
            _logger.error(f"Unexpected error occurred: {err}")

        return None

    def _create_attributes_for_product(self, template_data):
        if template_data['variants']:
            no_of_variants = len(template_data['variants'])
            if no_of_variants == 1:
                _logger.info(f"================================")
                _logger.info(f"No of variants: {no_of_variants}")
                _logger.info(f"================================")
                self.cr_product_uid = template_data['variants'][0]['productUid']
            if no_of_variants > 1:
                _logger.info(f"================================")
                _logger.info(f"No of variants: {no_of_variants}")
                _logger.info(f"================================")
                for variants in template_data['variants']:
                    exhisting_product_attribute_values = self.check_attribute_values(variants)
                    _logger.info(f"================================")
                    _logger.info(f"exhisting_product_attribute_values: {exhisting_product_attribute_values}")
                    _logger.info(f"================================")
                    for variant in self.product_variant_ids:
                        current_product_temp_attr_values = variant.product_template_attribute_value_ids.product_attribute_value_id
                        # corresponding_ptavs = variant.product_template_attribute_value_ids
                        # corresponding_pavs = corresponding_ptavs.product_attribute_value_id
                        if current_product_temp_attr_values == exhisting_product_attribute_values:
                            variant.cr_product_uid = variants['productUid']
                            break

                variants_having_no_gelato_product_id = self.env['product.product'].search([
                    ('product_tmpl_id', '=', self.id),
                    ('cr_product_uid', '=', False)
                ])
                variants_having_no_gelato_product_id.unlink()

    def check_attribute_values(self, variants):
        exhisting_product_attribute_values = self.env['product.attribute.value']
        # attributes = []
        # values = []
        _logger.info(f"================================befor")
        # _logger.info(f"attributes: {attributes}")
        # _logger.info(f"values: {values}")
        # Loop through each attribute option in the variant of the variants of gelato product
        for attribute_info in variants['variantOptions']:
            _logger.info(f"================================befor")
            _logger.info(f"attribute_info: {attribute_info}")
            # Search for an existing product attribute
            attribute = self.env['product.attribute'].search(
                [
                    ('name', '=', attribute_info['name']),
                    ('create_variant', '=', 'always')
                ],
                limit=1,
            )
            # if attribute.id not in attributes:
            #     _logger.info(f"================================")
            #     _logger.info(f"attribute: {attribute.id}")
            #     attributes.append(attribute.id)
            # If the attribute doesn't exist, create it
            if not attribute:
                attribute = self.env['product.attribute'].create({
                    'name': attribute_info['name']
                })
            _logger.info(f"================================")
            _logger.info(f"attribute: {attribute}")
            _logger.info(f"================================")
            # Search for an existing product attribute value
            attribute_value = self.env['product.attribute.value'].search([
                ('name', '=', attribute_info['value']),
                ('attribute_id', '=', attribute.id),
            ], limit=1)

            # if attribute_value.id not in values:
            #     _logger.info(f"================================")
            #     _logger.info(f"attribute_value: {attribute_value.id}")
            #     values.append(attribute_value.id)
            # If the attribute value doesn't exist, create it
            if not attribute_value:
                attribute_value = self.env['product.attribute.value'].create({
                    'name': attribute_info['value'],
                    'attribute_id': attribute.id
                })
            _logger.info(f"================================")
            _logger.info(f"exhisting_product_attribute_values: {exhisting_product_attribute_values}")
            _logger.info(f"================================")
            exhisting_product_attribute_values += attribute_value

            # Search for an existing product template attribute line value
            product_temp_attr_line = self.env['product.template.attribute.line'].search(
                [
                    ('product_tmpl_id', '=', self.id),
                    ('attribute_id', '=', attribute.id)
                ],
                limit=1,
            )
            # If the product template attribute line value doesn't exist, create it
            if not product_temp_attr_line:
                self.env['product.template.attribute.line'].create({
                    'product_tmpl_id': self.id,
                    'attribute_id': attribute.id,
                    'value_ids': [Command.link(attribute_value.id)]
                })
            else:
                product_temp_attr_line.value_ids = [Command.link(attribute_value.id)]

        # p = self.env['product.template.attribute.line'].search(
        #         [
        #             ('product_tmpl_id', '=', self.id),
        #         ],
        #         limit=1,
        #     )

        # _logger.info(f"================================after")
        # _logger.info(f"attributes: {attributes}")
        # _logger.info(f"values: {values}")

        # for data in p:
        #     _logger.info(f"================================ in data....")
        #     _logger.info(f"data: {data}")
        #     _logger.info(f"data.attribute_id: {data.attribute_id}")
        #     _logger.info(f"attributes: {attributes}")
        #     if data.attribute_id.id in attributes:
        #         _logger.info(f"data.attribute_id: {data.attribute_id}")
        #         for value in data.value_ids:
        #             _logger.info(f"value: {value}")
        #             if value.id in values:
        #                 _logger.info(f"in if")
        #                 _logger.info(f"value.id: {value.id}")
        #                 pass
        #             else:
        #                 _logger.info(f"in else")
        #                 _logger.info(f"value.id: {value.id}")
        #                 value.unlink()
        #     else:
        #         data.unlink()

        return exhisting_product_attribute_values

    def _create_print_images_for_product(self, template_data):
        image_info = template_data['variants'][0]['imagePlaceholders']
        for image_data in image_info:
            if image_data['printArea'].lower() in ('1', 'front'):
                image_data['printArea'] = 'default'

            is_image_found = bool(self.env['cr.product.doc'].search_count([
                ('name', 'ilike', image_data['printArea']),
                ('res_id', '=', self.id),
                ('res_model', '=', 'product.template'),
                ('is_gelato', '=', True),
            ]))
            _logger.info(f"================================")
            _logger.info(f"is_image_found: {is_image_found}")
            _logger.info(f"================================")
            if not is_image_found:
                self.cr_image_ids = [Command.create({
                    'name': image_data['printArea'].lower(),
                    'res_id': self.id,
                    'res_model': 'product.template',
                    'is_gelato': True,
                })]

    def msg_notification_from_gelato(self, msg):
        self.message_post(
            body=_("Notificaion from Gelato : %s" % msg),
        )
        if msg == 'store_product_template_updated':
            self.action_sync_gelato_template_info()
            self.store_product_template_updated()

    def is_temp_available(self, key):
        _logger.info(f"PRODUCT IN ================================")
        secret_key = self.env.user.company_id.webhook_secret_for_gelato
        # secret_key = self.env['ir.config_parameter'].sudo().get_param('webhook_secret_for_gelato')
        _logger.info(f"================================")
        _logger.info(f"key: {key}")
        _logger.info(f"secret_key: {secret_key}")
        _logger.info(f"================================")
        if secret_key == key:
            return True
        else:
            return False

    def open_gelato_template_wizard(self):
        # Get the template ID of the current product
        template_id = self.cr_template_ref
        _logger.info(f"================================")
        _logger.info(f"template_id: {template_id}")
        _logger.info(f"================================")
        # Open the wizard and fetch product details for the selected template
        wizard = self.env['gelato.template.wizard'].create({
            'template_id': template_id,  # assuming you have 'product_uid' in your template
        })
        _logger.info(f"================================")
        _logger.info(f"wizard: {wizard}")
        _logger.info(f"================================")
        # Fetch product details from the Gelato API
        wizard.fetch_template_details(template_id)

        # Open the wizard view
        return {
            'name': 'Gelato Template Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'gelato.template.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def set_img(self):
        _logger.info("============set_img called====================")
        api_key = self.env.user.company_id.api_key_for_gelato

        url = f'https://ecommerce.gelatoapis.com/v1/templates/{self.cr_template_ref}'

        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }

        response = requests.get(url, headers=headers)
        _logger.info(f"Response JSON: {response.json()}")
        _logger.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            template_data = response.json()
            image_url = template_data.get('previewUrl')

            if image_url:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    encoded_image = base64.b64encode(image_response.content)

                    for data in self.cr_image_ids:
                        _logger.info(f"cr_data: {data}")
                        if data.is_gelato:
                            _logger.info("CONDITION IS TRUE")
                            data.datas = encoded_image
                            self.image_1920 = encoded_image
                else:
                    _logger.info(f"Failed to download image from URL: {image_url}")
            else:
                _logger.info("No 'previewUrl' found in response.")
        else:
            _logger.error(f"Failed to get template data from Gelato API.")

    def apply_price(self, product_uid):
        api_key = self.env.user.company_id.api_key_for_gelato
        url = f'https://product.gelatoapis.com/v3/products/{product_uid}/prices'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }

        # Send GET request to Gelato API for product prices
        response = requests.get(url, headers=headers)
        _logger.info(f"response: {response.json()}")
        if response.status_code == 200:
            prices = response.json()
            _logger.info(f"Price data fetched: {prices}")
            lines = []
            for p in prices:
                if p.get('quantity') == 1:
                    return p.get('price')

    def create_store_product(self, data_info):
        image_url = data_info.get('previewUrl')

        if image_url:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                encoded_image = base64.b64encode(image_response.content)

                for data in self.cr_image_ids:
                    _logger.info(f"cr_data: {data}")
                    if data.is_gelato:
                        _logger.info("CONDITION IS TRUE")
                        data.datas = encoded_image
                        self.image_1920 = encoded_image
            else:
                _logger.warning(f"Failed to download image from URL: {image_url}")
        else:
            _logger.info("No 'previewUrl' found in response.")

        api_key = self.env.user.company_id.api_key_for_gelato
        storeId = data_info.get('storeId')
        productId = data_info.get('storeProductId')
        url = f'https://ecommerce.gelatoapis.com/v1/stores/{storeId}/products/{productId}'
        _logger.info(f"url: {url}")
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }

        response = requests.get(url, headers=headers)
        _logger.info(f"Response JSON: {response.json()}")
        _logger.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            template_data = response.json()
            self._create_attributes_for_store_product(template_data)

    def _create_attributes_for_store_product(self, template_data):
        for variants in template_data['productVariantOptions']:
            exhisting_product_attribute_values = self.check_attribute_values_for_store_product(variants)

        for variant in self.product_variant_ids:
            variant.cr_product_uid = self.assign_id_to_store_product(template_data, variant)

    def check_attribute_values_for_store_product(self, variants):
        _logger.info(f"================================check_attribute_values_for_store_product")
        exhisting_product_attribute_values = self.env['product.attribute.value']
        attribute = self.env['product.attribute'].search(
            [
                ('name', '=', variants['name']),
                ('create_variant', '=', 'always')
            ],
            limit=1,
        )

        if not attribute:
            attribute = self.env['product.attribute'].create({
                'name': variants['name']
            })
            _logger.info(f"================================")
            _logger.info(f"attribute: {attribute}")
            _logger.info(f"================================")

        for value in variants['values']:
            attribute_value = self.env['product.attribute.value'].search([
                ('name', '=', value),
                ('attribute_id', '=', attribute.id),
            ], limit=1)

            if not attribute_value:
                attribute_value = self.env['product.attribute.value'].create({
                    'name': value,
                    'attribute_id': attribute.id
                })
            _logger.info(f"================================")
            _logger.info(f"exhisting_product_attribute_values: {exhisting_product_attribute_values}")
            _logger.info(f"================================")
            exhisting_product_attribute_values += attribute_value

            # Search for an existing product template attribute line value
            product_temp_attr_line = self.env['product.template.attribute.line'].search(
                [
                    ('product_tmpl_id', '=', self.id),
                    ('attribute_id', '=', attribute.id)
                ],
                limit=1,
            )
            # If the product template attribute line value doesn't exist, create it
            if not product_temp_attr_line:
                self.env['product.template.attribute.line'].create({
                    'product_tmpl_id': self.id,
                    'attribute_id': attribute.id,
                    'value_ids': [Command.link(attribute_value.id)]
                })
            else:
                product_temp_attr_line.value_ids = [Command.link(attribute_value.id)]

        return exhisting_product_attribute_values

    def assign_id_to_store_product(self, template_data, variant):
        _logger.info(f"==============ppppppppp==================")
        _logger.info(f"variant: {variant}")
        _logger.info(f"================================")
        for record in variant.product_template_attribute_value_ids:
            _logger.info(f"record: {record}")
        # _logger.info(f"value_id: {variant.product_template_attribute_value_ids.product_attribute_value_id.name}")

        # for data in template_data['variants']:
        #     if data['title']:

    def store_product_template_updated(self):
        endpoint = f'templates/{self.cr_template_ref}'
        _logger.info(f"key >>>>>> {self.env.company.sudo().api_key_for_gelato} ")
        key = self.env.company.sudo().api_key_for_gelato
        template_data = self.gelato_api_request(endpoint, 'ecommerce', key, 'v1', 'GET')
        _logger.info(f"==========================================")
        _logger.info(f"template_data >>>>>> {template_data} ")
        _logger.info(f"==========================================")
        names = []
        values = []

        for variant in template_data['variants']:
            for option in variant.get('variantOptions', []):
                names.append(option['name'])
                values.append(option['value'])

        # for line in self.attribute_line_ids:
        #     for data in line.value_ids:
        #         if data.name in values:
        #             pass
        #         else:
        #            data.unlink()

    def create(self, vals):
        ref = super().create(vals)
        _logger.info("Creating %d record(s) with vals: %s", len(ref), vals)

        # Ensure vals is a list for consistency
        if not isinstance(vals, list):
            vals = [vals]

        for record, val in zip(ref, vals):
            record._customize_price(val)
            _logger.debug("Customized price for created record: %s", record.display_name)

        return ref

    def write(self, vals):
        _logger.info("Writing to %d record(s) with vals: %s", len(self), vals)

        ref = super().write(vals)

        if self.env.context.get("skip_update_fix_price", False):
            _logger.debug("Skipped _customize_price due to context flag.")
            return ref

        for record in self:
            record._customize_price(vals)
            _logger.debug("Customized price for updated record: %s", record.display_name)

        return ref

    def _customize_price(self, vals):
        if 'list_price' in vals:
            for variant in self.product_variant_ids:
                variant.cr_fix_price = vals['list_price']
                _logger.info(
                    "Set cr_fix_price for variant %s to %s",
                    variant.display_name,
                    vals['list_price']
                )





