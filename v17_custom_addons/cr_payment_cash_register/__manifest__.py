# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Payment Cash Register | Cash Register for Payments | Cash Register Payment System | Cash Register on Transactions",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "summary": """With the help of this app, your accounting staff can generate a direct cash register line, 
                or cash statement line of payment, for a customer or vendor who has a cash register or not.""",
    "version": "17.0.0.1",
    "summary": "",
    "sequence": 10,
    "description": """
    The accounting app allows users to efficiently manage cash transactions by providing two distinct methods for 
    creating cash statement lines.

    Using Cash Register: When processing payments from customer invoices or vendor bills, users can opt to utilize 
    an existing cash register. By selecting a pre-generated cash register, the system automatically creates a cash 
    statement line linked to that register.
    
    Without Using Cash Register: Alternatively, users can create cash statement lines without linking to a cash register. 
    This option is useful for situations where a cash register ID is not needed or when transactions need to be recorded independently. 
    The system will directly generate a cash statement line, simplifying the process for users who prefer not to use a cash register.
    
    Payment Cash Register
    Cash Register for Payments
    Cash Register Payment System
    Cash Register on Transactions
    Payments Cash Register
    Cash Register On Payments
    Payment Cash Register in odoo
    Cash Register for Payments in odoo
    Cash Register Payment System in odoo
    Cash Register on Transactions in odoo
    Payments Cash Register in odoo
    Cash Register On Payments in odoo
    """,
    "category": "accounting",
    "price": "108.72",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "account",'point_of_sale'],
    "data": [
        "views/view_account_payment_register_form.xml",
        "views/account_payment.xml",
        "views/account_bank_statement_line.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}