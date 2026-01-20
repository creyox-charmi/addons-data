# -*- coding: utf-8 -*-
{
    'name': "Website Blogs From Portal",
    'summary': """Website Blogs From Portal""",
    'description': """This section features blog articles originating from the portal, providing 
                      insights, updates, and information directly sourced from the platform
                   """,

    'sequence': 310,
    'version': '0.1',
    'depends': ['base', 'web', 'website_blog', 'portal', 'web_editor', 'http_routing', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_template.xml',
        'views/post_author_extension.xml',
        'views/ir_qweb_widget_templates.xml',
        'views/portal_message_template.xml',
        'views/blog_post_multimedia.xml',
        'views/blog_views.xml',
        'views/res.partner.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'wb_portal_blogs/static/src/js/wysiwyg_custom.js',
            'wb_portal_blogs/static/src/js/blog_form_preview.js',
            'wb_portal_blogs/static/src/js/search.js',
            'wb_portal_blogs/static/src/css/social_icons.css',
        ],
    },
    'license': 'LGPL-3'
}
