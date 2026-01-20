{
    'name': 'Smartsheet Connector',
    'version': '1.2',
    'summary': 'Configure approval settings for sales based on untaxed or total amount',
    'sequence': 10,
    'description': """
        This module allows configuration of sales approval based on either untaxed amount or total amount.
    """,
    'category': 'Accounting/Accounting',
    'website': '',
    'depends': ['base','contacts' ],
    'data': [
        'security/ir.model.access.csv',
        'views/cr_smartsheet_config.xml',
        'views/view_success_message.xml',
        'views/cr_inherit.xml',
        # 'views/sale_approval_line.xml',
        # 'views/my_approval.xml',
        # 'views/waiting_for_approval.xml',
        # 'wizard/sale_rejection_wizard.xml',
        # 'views/approval_info.xml',
        # 'views/sale_Quotation.xml',
        # 'settings/config_setting_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
