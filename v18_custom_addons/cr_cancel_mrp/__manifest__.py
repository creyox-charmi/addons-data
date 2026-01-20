# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Manufacturing Order Cancel | Manufacturing Order Reverse in Odoo | Manufacturing Order Reset to Draft in Odoo',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "mailto:support@creyox.com",
    'category': 'Manufacturing Order',
    'summary': 'Cancel/Reverse Manufacturing Order along with invoice & move history deletion',
    "license": "OPL-1",
    'version': '18.0',
    'description': """

Cancel/Reverse Manufacturing Order is module where when manufacturing order
can be cancelled along with it will delete invoice & move history for products
also the manufacturing order will have a Rest To Draft button to move 
manufacturing order into draft state.

Manufacturing Order Cancel in odoo,
Manufacturing Order Reverse in Odoo,
Manufacturing Order Reset to Draft in Odoo,

""",
    'depends': ["base", "mrp", "stock","account"],
    'data': [
        'views/mrp_cancel_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images": ["static/description/banner.png", ],
    "price": 80,
    "currency": "USD"
}
