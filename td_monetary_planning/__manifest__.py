# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

{
    'name': 'Monetary Planning for Odoo Gantt View',
    "version": "17.0.0.1",
    'category': 'Tools',
    'description': '''This module allow to add monetary planning for Odoo Gantt View''',
    'summary': '''This module allow to add monetary planning for Odoo Gantt View''',
    'depends': ['ks_gantt_view_project'],
    'data': ['views/project_task.xml'],
    'assets': {
        'web.assets_backend': [
            'td_monetary_planning/static/src/xml/**/*',
        ],
    },
    'application': True,
    'license': 'OPL-1',
}
