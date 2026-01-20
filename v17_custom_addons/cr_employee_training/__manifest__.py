{
    'name': 'Creyox Employee Training',
    'version': '1.2',
    'summary': '',
    'sequence': 10,
    'description': """
]

    """,
    'category': 'Accounting/Accounting',
    'website': '',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee.xml',
        'views/employee_training_record.xml',
        'views/training_session.xml',
        'views/employee_wizard.xml'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
