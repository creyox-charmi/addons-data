# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Case Study",
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
    "depends": ["base", "website"],
    "data": [
        'views/case_study_data.xml',
        'views/snippets.xml',
        'views/snippets/case_study.xml',
    ],
    'assets': {
        'website.assets_wysiwyg': [
            'cr_case_study/static/src/snippets/case_study/options.js',
        ],
    },

    "installable": True,
    "auto_install": False,
    "application": True,
}
