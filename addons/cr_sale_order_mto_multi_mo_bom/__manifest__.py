# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Sale Order MTO Multi MO BOM',
    'version': '18.0.0.1',
    'category': 'Sales',
    'summary': 'Create multiple MOs with hierarchical BOMs for RE orders',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    'depends': ['sale_stock', 'mrp', 'cr_sale_order_re_nre'],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}