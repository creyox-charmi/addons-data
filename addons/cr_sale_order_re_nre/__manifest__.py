# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    "name": "Sale Order RE NRE",
    "version": "18.0.0.12",
    "summary": "",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Sales",
    "depends": ["sale_management", "stock","account","sale_stock"],
    "data": [
        'views/product_product.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        "views/sale_order_line_re_sub.xml",
        "views/sale_order_line_nre_sub.xml",
        "wizard/sale_order_line_nre_sub_wizard.xml",
        "wizard/sale_order_line_re_sub_wizard.xml",
        'security/ir.model.access.csv',
    ],
"assets": {
        "web.assets_backend": [
            'cr_sale_order_re_nre/static/src/views/list/list_controller.xml',
        ],
    },
    "license": "OPL-1",
    "installable": True,
    "application": False,
}
