{
    'name': 'Inventory Management',
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
        'views/product.xml',
        'views/category.xml',
        'views/supplier.xml',
        'views/productWizard.xml'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
