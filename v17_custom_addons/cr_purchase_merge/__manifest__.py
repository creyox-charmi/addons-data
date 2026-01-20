{
    'name': 'Creyox Purchase Merge',
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
        'views/purchase_merge.xml',
        'views/purchase_wizard.xml'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
