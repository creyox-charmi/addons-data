# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Auto Set Dynamic Terms & Conditions in Sale Orders, Purchase Orders, & Invoicing | Default Set Terms & Conditions | Auto Translate Terms & Conditions",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "summary":
        """
            This module extends the the sale.order model in Odoo to manage Terms and Conditions (T&C) associated with sales orders. 
            It dynamically assigns T&C based on the selected customer, ensures default T&C are applied when no specific T&C exist, and allows 
            users to manually select their desired T&C.
            Auto Set Dynamic Terms & Conditions in Sale Orders, Purchase Orders, & Invoicing
            Auto Set Dynamic Terms & Conditions in Sale Orders, Purchase Orders, & Invoicing in odoo
            Default Set Terms & Conditions
            Default Set Terms & Conditions in odoo
            Auto Translate Terms & Conditions
            Auto Translate Terms & Conditions in odoo
            Automatically Configure Dynamic T&Cs for Sales, Purchases, & Invoices 
            Automatically Configure Dynamic T&Cs for Sales, Purchases, & Invoices in odoo
            Auto Assign Dynamic T&Cs for Sales, Purchases, & Invoices
            Auto Assign Dynamic T&Cs for Sales, Purchases, & Invoices in odoo
        """,
    "version": "17.0.0.1",
    "sequence": 10,
    "description":
        """
            This module is use to manage T&C within the sales order process. It automatically retrieves and sets the relevant T&C for each 
            Sale Order and Sale Order report, based on the customer. It applies default T&C if no T&C are applicable. It allows users to 
            manually select their desired T&C. Additionally, it features automatic translation capabilities, enhancing usability for 
            international customers.
        """,
    "category": "Sales",
    "price": "49",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "sale", "purchase", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/cr_terms_and_condition.xml",
        "views/res_config_settings.xml",
        "views/sale_order.xml",
        "views/purchase_order.xml",
        "views/account_move.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
