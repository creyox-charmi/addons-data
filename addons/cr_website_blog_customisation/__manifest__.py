# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Blog Customization",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "summary":
        """
        """,
    "version": "16.0.0.0",
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
        "data/color_data.xml",
        "views/cr_color.xml",
        "views/website_blog.xml",
        "views/website_blog_components.xml",
        "views/website_blog_posts_loop.xml",
        "views/website_blog_templates.xml",
        "views/snippets/random_blogs.xml",
        "views/snippets.xml",
        "security/ir.model.access.csv",
    ],
    'assets': {
        'web.assets_frontend': [
            'cr_website_blog_customisation/static/src/scss/website_blog.scss',
        ],
        'website.assets_wysiwyg': [
            'cr_website_blog_customisation/static/src/snippets/cr_random_blogs/options.js',
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
}
