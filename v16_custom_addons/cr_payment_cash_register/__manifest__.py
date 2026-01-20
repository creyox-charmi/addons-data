# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Payment Cash Register",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "17.0.0.1",
    "summary": "",
    "sequence": 10,
    "description": """
   
    """,
    "category": "accounting",
    "price": "15",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "account",'point_of_sale'],
    "data": [
        "views/view_account_payment_register_form.xml",
        "views/account_payment.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": [],
}