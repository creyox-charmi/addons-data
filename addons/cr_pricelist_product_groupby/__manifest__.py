# -*- coding: utf-8 -*-
{
    "name": "Product Pricelist Product Groupby",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Extra Tools",
    "summary": "Group product pricelist by name on the product form.",
    "license": "OPL-1",
    "version": "19.0.0.0",
    "depends": ["base", "stock", "product"],
    "data": [
        "views/product_template_views.xml",
    ],
'assets': {
        'web.assets_backend': [
            'cr_pricelist_product_groupby/static/src/**/*.js',
            'cr_pricelist_product_groupby/static/src/**/*.xml',
        ],
    },
    "installable": True,
    "application": False,
}
