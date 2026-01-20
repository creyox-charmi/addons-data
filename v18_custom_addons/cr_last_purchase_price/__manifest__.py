{
    'name': 'Costing Method: Last Purchase Price',
    'version': '18.0.1.0.0',
    'category': 'Warehouse',
    'summary': "Introducing new costing method in Odoo 'last purchase price'",
    'description': """Introducing new costing method in Odoo 
    'last purchase price'.The cost of the product changed based on the last 
    purchase order.""",
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'depends': ['purchase','stock_account', 'purchase_stock'],
    "data":  [
        'views/purchase_order.xml',
        'views/stock_move.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}