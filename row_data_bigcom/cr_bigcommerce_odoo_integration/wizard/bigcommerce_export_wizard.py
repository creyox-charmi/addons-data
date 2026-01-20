from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BigCommerceExportWizard(models.TransientModel):
    _name = 'bigcommerce.export.wizard'
    _description = 'BigCommerce Export Wizard'

    store_id = fields.Many2one('bigcommerce.store', string="Store", required=True, default=lambda self: self.env.context.get('default_store_id'))

    EXPORT_DATA_TYPES = [
        ('currency', 'Currencies'),
        ('product', 'Products'),
        ('customer', 'Customers'),
        ('customer_address', 'Customer Addresses'),
        ('location', 'Locations'),
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
        if self.export_data_type == 'currency':
            self.store_id.export_bigcommerce_currency()
        elif self.export_data_type == 'product':
            self.store_id.export_bigcommerce_products()
        elif self.export_data_type == 'customer':
            self.store_id.export_bigcommerce_customers()
        elif self.export_data_type == 'customer_address':
            self.store_id.export_bigcommerce_customer_addresses()
        elif self.export_data_type == 'location':
            self.store_id.export_bigcommerce_locations()
        elif self.export_data_type == 'inventory':
            self.store_id.export_bigcommerce_inventory()
        else:
            raise UserError(_("Export type not supported."))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Export Successful"),
                'message': _("{} exported to BigCommerce.").format(export_name),
                'type': 'success',
                'sticky': False,
            }
        }

