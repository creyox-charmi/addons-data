# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Odoo To BigCommerce Integration | BigCommerce Connector for Odoo | Odoo BigCommerce integration",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.1",
    "summary": """
        The BigCommerce Odoo Integration Module is a robust solution designed to seamlessly connect BigCommerce e-commerce 
        stores with Odoo ERP, enabling efficient two-way data synchronization. This module supports importing and exporting 
        critical business data, real-time updates via webhooks, scheduled actions for automation, and detailed logging 
        for all operations. It simplifies e-commerce operations, enhances inventory management, and ensures data consistency 
        across platforms, making it ideal for businesses seeking to streamline workflows and improve operational efficiency.
        
        Odoo To BigCommerce Integration
        BigCommerce Connector for Odoo
        Odoo BigCommerce integration
        Odoo connector for BigCommerce
        Real-time order sync BigCommerce to Odoo
        BigCommerce Odoo Bridge
        Odoo E-Commerce Sync
        
        BigCommerce Odoo integration module,
        Sync BigCommerce with Odoo ERP,
        Odoo BigCommerce connector features,
        Import orders from BigCommerce to Odoo,
        Export products from Odoo to BigCommerce,
        Odoo BigCommerce integration for inventory sync,
        How to automate BigCommerce orders in Odoo,
        Best module for Odoo BigCommerce product sync,
        Odoo BigCommerce real-time order import,
        Sync customer data between Odoo and BigCommerce,
        Odoo BigCommerce Store Flow,
        How to Set Up BigCommerce Store Data Export in Odoo,
        How to Integrate Odoo with BigCommerce Store for Order Syncing,
        Odoo BigCommerce Store Connector for Seamless Data Export,
        How to Import Orders from BigCommerce Store to Odoo,
        How to Sync Products from Odoo to BigCommerce Store Automatically,
        Real-Time Data Integration Between Odoo and BigCommerce Store,
        How to Configure BigCommerce Store Export Settings in Odoo,
        Best Practices for Exporting Odoo Data to BigCommerce Store,
        How to Handle Data Schema Mismatches Between Odoo and BigCommerce Store,
        Odoo BigCommerce Store Data Export Tool Setup Guide,
        Odoo BigCommerce Store Connector Installation Guide,
        What are the Best Tools for Odoo-BigCommerce Store Data Integration?,
        How to Schedule Odoo Data Exports to BigCommerce Store,
        Best BigCommerce Store Solution for Odoo,
        Odoo BigCommerce Store Integration Tutorial,
        Benefits of Using BigCommerce Store with Odoo,
        Seamless BigCommerce Store Integration with Odoo,
        BigCommerce Store Workflow Sync for Odoo,
        Odoo Real-Time BigCommerce Store Connector,
        BigCommerce Store Sync Tool for Odoo,
        Odoo BigCommerce Store Integration Solutions,
        BigCommerce Store Integration Hub for Odoo,
        BigCommerce Store-Odoo Workflow Solutions,
        BigCommerce Store Integration Solutions in Odoo
        """,
    "sequence": 10,
    "description": """
        The BigCommerce Odoo Integration Module is a robust solution designed to seamlessly connect BigCommerce e-commerce 
        stores with Odoo ERP, enabling efficient two-way data synchronization. This module supports importing and exporting 
        critical business data, real-time updates via webhooks, scheduled actions for automation, and detailed logging 
        for all operations. It simplifies e-commerce operations, enhances inventory management, and ensures data consistency 
        across platforms, making it ideal for businesses seeking to streamline workflows and improve operational efficiency.
        
        Odoo To BigCommerce Integration
        BigCommerce Connector for Odoo
        Odoo BigCommerce integration
        Odoo connector for BigCommerce
        Real-time order sync BigCommerce to Odoo
        BigCommerce Odoo Bridge
        Odoo E-Commerce Sync
        
        BigCommerce Odoo integration module,
        Sync BigCommerce with Odoo ERP,
        Odoo BigCommerce connector features,
        Import orders from BigCommerce to Odoo,
        Export products from Odoo to BigCommerce,
        Odoo BigCommerce integration for inventory sync,
        How to automate BigCommerce orders in Odoo,
        Best module for Odoo BigCommerce product sync,
        Odoo BigCommerce real-time order import,
        Sync customer data between Odoo and BigCommerce,
        Odoo BigCommerce Store Flow,
        How to Set Up BigCommerce Store Data Export in Odoo,
        How to Integrate Odoo with BigCommerce Store for Order Syncing,
        Odoo BigCommerce Store Connector for Seamless Data Export,
        How to Import Orders from BigCommerce Store to Odoo,
        How to Sync Products from Odoo to BigCommerce Store Automatically,
        Real-Time Data Integration Between Odoo and BigCommerce Store,
        How to Configure BigCommerce Store Export Settings in Odoo,
        Best Practices for Exporting Odoo Data to BigCommerce Store,
        How to Handle Data Schema Mismatches Between Odoo and BigCommerce Store,
        Odoo BigCommerce Store Data Export Tool Setup Guide,
        Odoo BigCommerce Store Connector Installation Guide,
        What are the Best Tools for Odoo-BigCommerce Store Data Integration?,
        How to Schedule Odoo Data Exports to BigCommerce Store,
        Best BigCommerce Store Solution for Odoo,
        Odoo BigCommerce Store Integration Tutorial,
        Benefits of Using BigCommerce Store with Odoo,
        Seamless BigCommerce Store Integration with Odoo,
        BigCommerce Store Workflow Sync for Odoo,
        Odoo Real-Time BigCommerce Store Connector,
        BigCommerce Store Sync Tool for Odoo,
        Odoo BigCommerce Store Integration Solutions,
        BigCommerce Store Integration Hub for Odoo,
        BigCommerce Store-Odoo Workflow Solutions,
        BigCommerce Store Integration Solutions in Odoo
        """,
    "category": "Extra Tools",
    "price": 500,
    "currency": "USD",
    "license": "OPL-1",
    "depends": ["sale_management", "stock", "delivery", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/big_commerece_menuitem.xml",
        "views/bigcommerce_store.xml",
        "views/product_category.xml",
        "views/res_partner.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/sale_order.xml",
        "views/bigcommerce_order_status_views.xml",
        "views/bigcommerce_brand.xml",
        "views/stock_location.xml",
        "views/bigcommerce_shipping_zone.xml",
        "views/delivery_carrier.xml",
        "views/res_currency.xml",
        "views/bigcommerce_webhook.xml",
        "views/account_tax.xml",
        "views/account_fiscal_position.xml",
        "wizard/select_store.xml",
        "views/logs.xml",
        "views/stock_picking.xml",
        "wizard/bigcommerce_import_wizard.xml",
        "wizard/bigcommerce_export_wizard.xml",
        "wizard/bigcommerce_import_progress_wizard_view.xml",
        "views/account_fiscal_position_postal.xml"
    ],
'assets': {
    'web.assets_backend': [
        'cr_bigcommerce_odoo_integration/static/src/js/import_progress.js',
        'cr_bigcommerce_odoo_integration/static/src/js/import_progress.xml',
    ],
},
    "post_init_hook": "_post_init_hook",
    "installable": True,
    "auto_install": True,
    "application": True,
    "images": ["static/description/banner.png"],
}
