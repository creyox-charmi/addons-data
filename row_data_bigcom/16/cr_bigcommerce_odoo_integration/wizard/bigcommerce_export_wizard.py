# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BigCommerceExportWizard(models.TransientModel):
    _name = 'bigcommerce.export.wizard'
    _description = 'BigCommerce Export Wizard'

    store_id = fields.Many2one('bigcommerce.store', string="Store", required=True, default=lambda self: self.env.context.get('default_store_id'))

    EXPORT_DATA_TYPES = [
        ('categories', 'Categories'),
        ('product', 'Products'),
        ('customer', 'Customers'),
        ('customer_address', 'Customer Addresses'),
        ('inventory', 'Inventory'),
    ]

    export_data_type = fields.Selection(
        selection=EXPORT_DATA_TYPES,
        string="Export Data Type",
        required=True,
    )

    def action_export(self):
        self.ensure_one()

        # Map selected type to human-readable name
        export_name = dict(self._fields['export_data_type'].selection).get(self.export_data_type)

        # Perform export based on selected type
        if self.export_data_type == 'categories':
            self.store_id.action_export_categories_to_bigcommerce()
        elif self.export_data_type == 'product':
            self.store_id.action_export_products_to_bigcommerce()
        elif self.export_data_type == 'customer':
            self.store_id.action_export_customers_to_bigcommerce()
        elif self.export_data_type == 'customer_address':
            self.store_id.action_export_customer_addresses()
        elif self.export_data_type == 'inventory':
            self.store_id.bulk_export_inventory()
        else:
            raise UserError(_("Export type not supported."))


