{
    'name': 'Mail Template Scheduler',
    'version': '18.0.0.1',
    'category': 'Tools',
    'summary': 'Add scheduling capability to mail templates for multiple users',
    'description': """
        This module extends mail templates with:
        - Multiple user selection
        - Frequency configuration
        - Automatic scheduled action creation
    """,
    'depends': ['mail', 'base'],
    'data': [
        'views/mail_template_view.xml',
        "views/template.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}