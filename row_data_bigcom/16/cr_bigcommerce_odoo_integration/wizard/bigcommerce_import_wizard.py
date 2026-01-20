# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BigCommerceImportWizard(models.TransientModel):
    _name = 'bigcommerce.import.wizard'
    _description = 'BigCommerce Import Wizard'

    store_id = fields.Many2one('bigcommerce.store', string="Store", required=True, default=lambda self: self.env.context.get('default_store_id'))

    IMPORT_DATA_TYPES = [
        ('currency', 'Currencies'),
        ('category', 'Product Categories'),
        ('brand', 'Brands'),
        ('product', 'Products'),
        ('customer', 'Customers'),
        ('customer_address', 'Customer Addresses'),
        ('tax', 'Tax Rates'),
        ('location', 'Locations'),
        ('shipping_zone', 'Shipping Zones'),
        ('inventory', 'Inventory'),
        ('order_status', 'Order Statuses'),
        ('order', 'Orders'),
    ]

    import_data_type = fields.Selection(
        selection=IMPORT_DATA_TYPES,
        string="Import Data Type",
        required=True,
    )
    is_import_order_by_date = fields.Boolean(string="Import Order Using Dates?")
    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')

    def action_import(self):
        self.ensure_one()
        store = self.store_id

        # Find human-readable label
        selected_label = dict(self.IMPORT_DATA_TYPES).get(self.import_data_type, "Selected Data")

        # Dispatch import methods
        if self.import_data_type == 'category':
            store.action_import_bigcommerce_categories()
        elif self.import_data_type == 'brand':
            store.action_import_bigcommerce_brands()
        elif self.import_data_type == 'product':
            store.import_bigcommerce_products()
        elif self.import_data_type == 'customer':
            store.action_import_bigcommerce_customers()
        elif self.import_data_type == 'customer_address':
            store.action_import_bigcommerce_customer_addresses()
        elif self.import_data_type == 'order':
            if self.is_import_order_by_date:
                self.store_id.action_import_bigcommerce_orders_by_date(
                    from_date=self.from_date,
                    to_date=self.to_date,
                )
            else:
                self.store_id.action_import_bigcommerce_orders()
        elif self.import_data_type == 'order_status':
            store.action_import_order_statuses()
        elif self.import_data_type == 'shipping_zone':
            store.action_import_shipping_zones()
        elif self.import_data_type == 'currency':
            store.action_import_bigcommerce_currencies()
        elif self.import_data_type == 'location':
            store.action_import_inventory_locations()
        elif self.import_data_type == 'tax':
            store.action_sync_taxes()
        elif self.import_data_type == 'inventory':
            store.action_sync_inventory()
        else:
            raise UserError(_("Invalid import type selected."))

