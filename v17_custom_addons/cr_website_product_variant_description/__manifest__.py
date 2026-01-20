# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Website Product Variant Description',
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
    'category': 'Website',
    "price": "",
    "currency": "USD",
    "license": "AGPL-3",
    'depends': ['website', 'website_sale','product','web'],
    'data': [
    "views/product_product.xml",
    "views/template.xml"
    ],
'assets': {
        'web.assets_frontend': [
            'cr_website_product_variant_description/static/src/js/product_description.js'
        ],
},
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
