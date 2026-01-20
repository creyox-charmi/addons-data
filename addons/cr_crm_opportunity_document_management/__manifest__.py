{
    'name': "CRM Opportunity Document Management",
    'version': '18.0.0.5.0',
    'category': 'Sales/CRM',
    "license": "OPL-1",
    'summary': 'Manages document folder structure for CRM opportunities',
    'depends': ['crm', 'documents'],
    'data': [
        'security/ir.model.access.csv',
        'data/documents_folder_data.xml',
        'views/crm_lead_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}
