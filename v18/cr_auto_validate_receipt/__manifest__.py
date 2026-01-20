# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Auto Validate Receipt',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0",
    'summary':
        """

        """,
    "sequence": 10,
    "description":
        """

        """,
    'category': '',
    "price": "",
    "currency": "USD",
    "license": "OPL-1",
    'depends': ['base', 'purchase', 'cr_scrap_management'],
    'data': [
        'views/po_group.xml',
        'views/purchase_order.xml'
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
