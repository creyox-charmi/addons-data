# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    "name": "Sale Order RE NRE",
    "version": "18.0",
    "summary": "",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Sales",
    "depends": ["sale","stock"],
    "data": [
'views/sale_order_views.xml',
        "views/sale_order_line_re_sub.xml",
        "views/sale_order_line_nre_sub.xml",
"wizard/sale_order_line_nre_sub_wizard.xml",
        'security/ir.model.access.csv',
    ],
    "license": "OPL-1",
    "installable": True,
    "application": False,
}
