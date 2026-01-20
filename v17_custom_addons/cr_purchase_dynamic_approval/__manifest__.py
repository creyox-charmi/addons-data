{
    'name': ' Purchase Dynamic Approval',
    'version': '1.2',
    'summary': '',
    'sequence': 10,
    'description': """

    """,
    'category': 'Accounting/Accounting',
    'website': '',
    'depends': ['base','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/approval_configuration.xml',
        'views/approval_details.xml',
        'views/add_page.xml',
        'views/setting_config.xml',
        'views/cr_my_approval.xml',
        'views/cr_waiting_approval.xml',
        'views/approval_info_line.xml',
        'views/cr_reject_wizard.xml'

    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
