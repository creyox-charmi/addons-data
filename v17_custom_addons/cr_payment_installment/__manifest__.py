# -*- coding: utf-8 -*-
# Part of Creyox technologies.

{
    "name": "Payment Installments | Sale Installments | Invoice Installments",
    "summary": """This module used to make payment in installments wise in sale and invoice,
    User can set tenure(month), installment amount, different down payments and print sale and invoice installment reports. 
    """,
    "description": """
        Installment,
        Payment Installments,
        Installment in sale,
        Installment in invoice,
        Sale Installment,
        Invoice Installment,
        Installment wise payment in sale,
        Installment wise payment in invoice,
        Make Installment payment in sale,
        Make Installment payment in invoice
        Payment Installment in odoo
        Installment Payment in odoo
        Installment in odoo
    """,
    "category": "Sales",
    "author": "Creyox Technologies",
    "website": "https://creyox.com",
    "depends": ["base", "account", "sale_management"],
    "vesion": "17.0",
    "price": "50.0",
    "currency": "USD",
    "license": "OPL-1",
    "images": ["static/description/banner.png"],
    "data": [
        "data/cron.xml",
        "data/data.xml",
        "security/ir.model.access.csv",
        "security/access.xml",
        "wizard/create_part_payment.xml",
        "views/account_payment_installment_view.xml",
        "views/sale_payment_installment_view.xml",
        "report/report_action.xml",
        "report/report_installment.xml",
        "report/report_invoice_installment.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
