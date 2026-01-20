# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Odoo To BigCommerce Integration | BigCommerce Connector for Odoo ',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "17.0",
    'summary':
        """
        """,
    "sequence": 10,
    "description":
        """
        """,
    'category': 'Extra Tools',
    "price": '',
    "currency": "USD",
    "license": "OPL-1",
    'depends': ['sale', 'stock', 'delivery', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/big_commerece_menuitem.xml',
        'views/bigcommerce_store.xml',
        'views/product_category.xml',
        'views/res_partner.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'views/sale_order.xml',
        'views/bigcommerce_order_status_views.xml',
        'views/bigcommerce_brand.xml',
        # 'views/bigcommerce_currency.xml',
        'views/stock_location.xml',
        'views/bigcommerce_shipping_zone.xml',
        # 'views/bigcommerce_shipping_method.xml',
        'views/delivery_carrier.xml',
        'views/res_currency.xml',
        'views/bigcommerce_webhook.xml',
        'views/account_tax.xml',
        'views/account_fiscal_position.xml',
        'wizard/select_store.xml',
        'views/logs.xml',
        'views/stock_picking.xml',
        'wizard/bigcommerce_import_wizard.xml',
        'wizard/bigcommerce_export_wizard.xml'
    ],
    'post_init_hook': '_post_init_hook',
    "installable": True,
    "auto_install": True,
    "application": True,
    "images": ["static/description/banner.png"],
}
