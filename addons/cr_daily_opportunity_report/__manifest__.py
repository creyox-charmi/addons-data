# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Daily Opportunity Report',
    'version': '18.0.0.4',
    'category': 'CRM',
    'summary': 'Automatic daily template report of won-lost opportunities',
    'author': 'Creyox Technologies',
    'website': 'https://www.creyox.com',
    'support': 'support@creyox.com',
    'depends': ['crm', 'base'],
    'data': [
        # 'data/cron_data.xml',
        'data/mail_template_data.xml',
        'views/res_users_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}