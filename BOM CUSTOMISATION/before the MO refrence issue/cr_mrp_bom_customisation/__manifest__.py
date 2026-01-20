# __manifest__.py
{
    'name': 'MRP BOM EVR Customization',
    'version': '18.0',
    'summary': 'Add EVR field customization to BOM overview',
    'description': """
        This module adds EVR customization to BOM:
        - Adds is_evr boolean field to BOM
        - Auto-sets is_evr to True when product internal ref starts with 'EVR'
        - Hides project_id field when is_evr is False
        - Displays EVR badge in BOM overview report
    """,
    'category': 'Manufacturing',
    'depends': ['mrp', 'project','purchase','stock','purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_view.xml',
    ],
   'assets': {
        'web.assets_backend': [
            'cr_mrp_bom_customisation/static/src/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}