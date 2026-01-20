# -*- coding: utf-8 -*-

{
    'name': 'Website Customisation',
    'version': '16.0.8.0.0',
    'category': 'Website',
    'summary': 'Terms and Conditions confirmation for blog publishing',
    'description': """This module adds terms and conditions confirmation popup before saving blog posts with dynamic content management.""",
    'depends': ['wb_portal_blogs', 'website', 'portal', 'website_blog'],
    'data': [
        'security/ir.model.access.csv',
        'views/blog_tag_category.xml',
        'views/blog_blog.xml',
        #'views/blog_available_category.xml',
        'views/terms_condition_views.xml',
        'views/portal_blog_templates.xml',
        'data/terms_condition_data.xml',
        'views/portal_breadcrumb.xml',
        'views/mail_message.xml',
        'views/portal_blog_category_filter_templates.xml',
        'views/blog_post_views.xml',
        'views/template.xml',
        'views/portal_messages_templates.xml',
        'views/portal_template.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'td_website_customisation/static/src/js/portal_blog_confirmation.js',
            'td_website_customisation/static/src/css/portal_blog_confirmation.css',
            'td_website_customisation/static/src/css/blog_category_filter.css',
            'td_website_customisation/static/src/js/blog_category_filter.js',
            'td_website_customisation/static/src/js/portal_messages.js',
            'td_website_customisation/static/src/css/portal_messages.css'
        ],
    },
    'author': 'Rohan & Bhavik',
    'website': 'http://www.tidyway.in',
    'license': 'OPL-1',
    'application': True,

}
