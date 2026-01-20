# -*- coding: utf-8 -*-

{
    "name": "Employee Extension",
    "category": 'Employee',
    "summary": """
       Adding features in Employee Modules 
       product.""",
    "description": """

    This module is use to create Product Bundle,Product Pack, 
    Bundle Pack of Product, Combined Product pack.
    -Product Pack, Custom Combo Product, Bundle Product. Customized product,
    Group product.Custom product bundle. Custom Product Pack.
    -Pack Price, Bundle price, Bundle Discount, Bundle Offer.
    """,
    "sequence": 1,
    "author": "Werpsol",
    "website": "http://www.werpsol.in",
    "version": '14.0.0.1',
    "depends": ['hr', 'hr_contract', 'base_iban', 'hr_skills','hr_timesheet', 'hr_gamification', 'employee_documents_expiry'],
    "data": [
        'views/employee.xml',
        'views/employee_contract.xml',
       # 'data/sequence.xml',
        'demo/employee_demo.xml',
        'security/ir.model.access.csv',

    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
