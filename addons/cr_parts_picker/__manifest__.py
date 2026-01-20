# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Parts Picker",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0",
    "summary": """
        """,
    "sequence": 10,
    "description": """
        """,
    "category": "eCommerce",
    "price": "",
    "currency": "USD",
    "license": "OPL-1",
    "depends": ["base", "website_sale", "product", "stock"],
    "data": [
        "data/data.xml",
        "views/template.xml",
        "views/product_public_category.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "cr_parts_picker/static/src/js/parts_picker_ui.js",
            "cr_parts_picker/static/src/js/products.js",
            "cr_parts_picker/static/src/scss/category.scss",
        ]
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
