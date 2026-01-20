# -*- coding: utf-8 -*-

{
    "name": "Sale Dynamic Approval | Sale Order Dynamic Approval | Quotation Dynamic Approval | Dynamic Sale Approval | Sale Approval Process | Sale Order Approval Process",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Sales",
    "summary": "Dynamic Sale Order Approval,Dynamic Sales Approval,Sales Multi Approval,Sale Order Multiple Approval,Quotaion Dynamic Approval,Sale Order Double Approval,Sale Double Approval,Sale User Dynamic Approval,User Wise Approval,Group Wise Approval Odoo",
    "description": """This module allows you to set dynamic and multi-level approvals in quotation/sale order so each order can be approved by many levels. Sale orders can be approved based on untaxed/ total amount and approved by particular users or groups they get emails notification about orders that waiting for approval. When a sale order approves or rejects salesperson gets a notification about it.
""",
    "version": "16.0.1",
    "depends": ["sale_management", "bus","sh_base_dynamic_approval"],
    "data": [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'wizard/rejection_wizard_views.xml',
        'views/sale_approval_config_views.xml',
        'views/sale_approval_line_views.xml',
        'views/res_config_setting_views.xml',
        'views/sale_order_views.xml',
        'views/approval_info_views.xml',

    ],
   
    "auto_install": False,
    "installable": True,
    "application": True,
    "license": "OPL-1",
    "images": ["static/description/background.png", ],
    "price": 30,
    "currency": "EUR"
}
