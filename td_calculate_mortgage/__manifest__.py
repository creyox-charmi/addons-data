# -*- coding: utf-8 -*-
{
    'name': 'Mortgage',
    "author": "TidyWay Software Solutions",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "17.0",
    'summary':
        """
        TidyWay Mortgage
        """,
    "sequence": 10,
    "description":
        """
        TidyWay Mortgage
        """,
    'category': 'Website',
    "price": '',
    "currency": "USD",
    "license": "AGPL-3",
    'depends': ['website', ],
    'data': [
        "security/ir.model.access.csv",
        "views/cr_mortgage.xml",
        'views/snippets.xml',
        "views/snippets/cr_mortgage.xml",

    ],
    "installable": True,
    "auto_install": True,
    "application": True,
}
