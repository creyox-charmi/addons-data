# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Snippet for display related blogs",
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
    "depends": ["base", "website", "website_blog"],
    "data": [
        "views/snippets/random_blogs.xml",
        "views/snippets.xml",
    ],
    'assets': {
        'website.assets_wysiwyg': [
            'cr_randomly_pick_blogs_snippet/static/src/snippets/cr_random_blogs/options.js',
        ],
    },

    "installable": True,
    "auto_install": False,
    "application": True,
}
