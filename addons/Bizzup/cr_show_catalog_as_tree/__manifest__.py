# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    'name': 'Sale Catalog View Customization',
    'version': '18.0.0.0',
    'category': 'Sales',
    'summary': 'Toggle between Kanban and Tree View for product catalog in sales orders',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Sales",
    'depends': ['sale', 'base','product'],
    'data': [
        'views/res_company_views.xml',
        'views/product_product_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cr_show_catalog_as_tree/static/src/js/catalog_quantity_widget.js',
            'cr_show_catalog_as_tree/static/src/xml/catalog_quantity_widget.xml',
            'cr_show_catalog_as_tree/static/src/css/catalog_tree.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}