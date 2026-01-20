# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Website Customisation",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "summary":
        """
        """,
    "version": "16.0.0.1",
    "sequence": 10,
    "description":
        """
        """,
    "category": "website",
    "price": "",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "website",],
    "data": [
        "security/ir.model.access.csv",
        "views/cr_client.xml",
        "views/snippets/explore_clients.xml",
        "views/snippets.xml",
    ],
'assets': {
    'website.assets_wysiwyg': [
        'cr_website_customization/static/src/snippets/explore_clients/options.js',
    ],
},


    "installable": True,
    "auto_install": False,
    "application": True,
}
