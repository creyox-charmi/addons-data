{
    'name': 'Training Module',
    'version': '1.2',
    'summary': '',
    'sequence': 10,
    'description': """

    """,
    'category': 'Accounting/Accounting',
    'website': '',
    'depends': ['base','mail','hr','sale'],
    'data': [
        'views/groups.xml',
        'security/ir.model.access.csv',
        'views/department.xml',
        'views/student.xml',
        'views/employee.xml',
        'views/departmentWizard.xml',
        'views/sale_order_line.xml',
        'views/sale_order.xml',
        'views/split_sale_wizard.xml',
        'report/department_report.xml',
        'report/custome_header.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
