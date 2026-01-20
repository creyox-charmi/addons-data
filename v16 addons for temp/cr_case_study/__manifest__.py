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
    "depends": ["base", "website", 'cr_website_customization'],
    "data": [
        'views/case_study_data.xml',
        'views/snippets.xml',
        'views/snippets/case_study.xml',
        "views/case_study_main_template.xml",

    ],
    'assets': {
        'website.assets_wysiwyg': [
            'cr_case_study/static/src/snippets/case_study/options.js',
        ],
        'web.assets_frontend': [
            'cr_case_study/static/src/scss/case_study.scss',
        ],
    },

    "installable": True,
    "auto_install": False,
    "application": True,
}
