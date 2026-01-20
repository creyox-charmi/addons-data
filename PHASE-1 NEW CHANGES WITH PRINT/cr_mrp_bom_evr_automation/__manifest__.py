# -*- coding: utf-8 -*-
{
    'name': 'MRP BOM EVR Automation',
    'version': '18.0.1.0',
    'summary': 'Automated procurement and transfer flow for EVR BOMs',
    'category': 'Manufacturing',
    'license': 'LGPL-3',
    'author': 'Creyox Technologies',
    'website': 'https://www.creyox.com',
    'depends': [
        'cr_mrp_bom_customisation',
        'cr_mrp_bom_evr_customisation',
    ],
    'data': [
        'data/ir_cron_data.xml',
        # 'views/mrp_bom_line_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}