# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Website Sticky Button',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "17.0",
    'summary':
        """
        """,
    "sequence": 10,
    "description":
        """
        """,
    'category': 'website',
    "price": '',
    "currency": "USD",
    "license": "OPL-1",
    'depends': ['base','website','web_editor',],
    'data': [],
    'assets': {
            'web_editor.assets_wysiwyg': [
                'cr_website_sticky_button/static/src/xml/web_editor.xml',
                'cr_website_sticky_button/static/src/js/wysiwyg/widgets/**/*',
            ],
            'website.assets_all_wysiwyg': [
                ('include', 'web_editor.assets_wysiwyg'),
            ],
        },
    "installable": True,
    "auto_install": True,
    "application": True,
    "images": ["static/description/banner.png"],
}
