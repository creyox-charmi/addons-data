# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Scrap Management',
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
    'depends': ['base', 'purchase', 'account', 'stock'],
    'data': [

        'views/groups.xml',
        'security/ir.model.access.csv',
        'views/scrap_management_menus.xml',
        'views/purchase_order.xml',
        'report/paper.xml',
        'views/report.xml'
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
