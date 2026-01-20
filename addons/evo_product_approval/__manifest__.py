# -*- coding: utf-8 -*-
{
    'name': 'Product Approval',
    'summary': "Product Approval, Product,Desigantion Wise Approval, Approval Level Setup, Approve and Reject Request,Send For Approval ",
    'category': 'Tools',
    'version': '18.0',
    'sequence': 11,
    'author': 'Evozard',
    'website': 'http://evozard.com/',
    'license': 'OPL-1',
    'price': 19.99,
    'currency': 'USD',
    'support': 'support@evozard.com',
    'description': """
            This Module is suitable for business where approval is required to create a Product. Administrator can set up levels of approval for creating Prouduct . Administrator can define the approval levels, like first, second, third.... Administrator can set up that who will be the approver of each level in terms of designation, like Team Leader, Sales Manager, etc.
    """,
    'depends': ['base', 'stock', 'hr_recruitment','sale','hr'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_approval_wiz_view.xml',
        'wizard/product_reject_wiz_view.xml',
        'view/product_approval_master.xml',
        'view/product_inherit.xml',
        'view/menu.xml',
    ],
    'images': ["static/description/banner.png"],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': True,
    'demo': [],
    'test': []
}
