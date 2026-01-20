# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    "name": "Sale Order Create Type",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "17.0",
    "category": "Sales",
    "summary": "Add dropdown on Create button in Sale Orders for B2B / B2C",
    "description": """
        This module customizes the Sale Order list view:
        - Replaces default Create button with a dropdown
        - Options: B2B (order type = Kronos), B2C (order type = Kronos Lab)
    """,
    "depends": ["sale_management"],
     "data": [
        "views/sale_order.xml",
    ],
     "assets": {
        "web.assets_backend": [
            'cr_sale_order_type_selector/static/src/views/**/*',
            'cr_sale_order_type_selector/static/src/xml/add_search.xml',
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
}
