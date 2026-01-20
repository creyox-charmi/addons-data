# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

{
    "name": "Payment on Sale | Customer Payment on Sale | Register Payment From Sale Order",
    "summary": """This module used to register customer payment from the sale order.
    User can see payment directly from the sales order
    """,
    "description": """
        Payment,
        Customer Advance Payment On Sale,
        Advance Payment on Sale Quotation,
        Payment on Sale,
        Register Payment From Sale Order,
        Sale Order Advance Payment,
        Payment Register in sale order,
    """,
    "category": "Sales",
    "author": "Creyox Technologies",
    "website": "https://creyox.com",
    "depends": ["base", "account", "sale_management"],
    "vesion": "18.0",
    "price": "50.0",
    "currency": "USD",
    "license": "OPL-1",
    "images": ["static/description/banner.png"],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/account_payment.xml',
        'views/sale_order_views.xml',
        'wizard/cr_register_payment_wizard_views.xml'
    ],
     'assets': {
        'web.assets_backend': [
            'cr_payment_on_sales/static/src/**/*',
        ]
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
