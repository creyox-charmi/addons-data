# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Chatter Message Cancel',
    'version': '18.0.0.0',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    'category': 'Discuss',
    'summary': 'Cancel messages in chatter with strikethrough',
    'depends': ['mail'],
    'assets': {
        'web.assets_backend': [
            'cr_chatter_message_cancel/static/src/js/message_cancel.js',
            'cr_chatter_message_cancel/static/src/xml/message_cancel.xml',
            'cr_chatter_message_cancel/static/src/css/message_cancel.scss',
        ],
    },
    "license": "OPL-1",
    "installable": True,
    'auto_install': False,
    'application': False,
}