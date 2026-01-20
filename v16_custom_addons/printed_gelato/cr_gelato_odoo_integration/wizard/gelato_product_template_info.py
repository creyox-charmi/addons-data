from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class GelatoTemplateWizard(models.TransientModel):
    _name = 'gelato.template.wizard'
    _description = 'Gelato Template Wizard'

    template_id = fields.Char(string='Template ID', required=True)
    template_name = fields.Char(string='Template Name')
    description = fields.Html(string='Description')
    preview_url = fields.Char(string='Preview URL')
    product_type = fields.Char(string='Product Type')
    vendor = fields.Char(string='Vendor')
    variants = fields.Text(string='Variants')

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(GelatoTemplateWizard, self).default_get(fields_list)

    #     # Get the template_id from context (passed when opening the wizard)
    #     template_id = self.env.context.get('default_template_id')
    #     _logger.info(f"template_id {template_id}")
    #     if template_id:
    #         res['template_id'] = template_id
    #         self.fetch_template_details(template_id)  # Fetch template details right away

    #     return res

    def fetch_template_details(self, template_id):
        # Replace with actual API Key
        api_key = self.env.user.company_id.api_key_for_gelato
        _logger.info(f"Fetching details for template_id {template_id}")

        # API Endpoint for retrieving template details
        url = f'https://ecommerce.gelatoapis.com/v1/templates/{template_id}'

        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }

        # Send GET request to Gelato API
        response = requests.get(url, headers=headers)
        _logger.info(f"Response JSON: {response.json()}")
        _logger.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            template_data = response.json()

            # Use write method to update the fields in the wizard
            self.template_name = template_data.get('templateName')
            self.description = template_data.get('description')
            self.preview_url = template_data.get('previewUrl')
            self.product_type = template_data.get('productType')
            self.vendor = template_data.get('vendor')
            self.variants = json.dumps(template_data.get('variants', []), indent=4)
        else:
            raise ValueError(f"Failed to fetch template data: {response.text}")
