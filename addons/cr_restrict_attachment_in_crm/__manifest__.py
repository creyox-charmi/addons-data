# -*- coding: utf-8 -*-
{
    'name': 'CRM Restrict Attachment in Chatter',
    'version': '18.1',
    'category': 'CRM',
    'summary': 'Hide attachment functionality completely from chatter',
    'description': """
        This module completely hides the attachment functionality from the chatter including:
        - Attachment button/icon
        - Drag and drop functionality
        - File upload options
        - Attachment preview
    """,
     "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    'depends': ['base', 'mail', 'crm'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'cr_restrict_attachment_in_crm/static/src/js/chatter_restrict_attachment.js',
            'cr_restrict_attachment_in_crm/static/src/xml/chatter.xml',
            'cr_restrict_attachment_in_crm/static/src/js/composer.js',
            'cr_restrict_attachment_in_crm/static/src/xml/composer.xml',
        ],
    },
    "license": "OPL-1",
    "installable": True,
    'auto_install': False,
    'application': False,
}