# -*coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": """HR Attendance Break | Attendance Pause | HR Attendance Lunch Time | Attendance Lunch Break""",
    "summary": """
        The Odoo users can pause and resume HR attendances on check-in/check-out and kiosk with this module.
    """,
    "version": "17.1",
    "description": """
        The Odoo users can pause and resume HR attendances on check-in/check-out and kiosk with this module.
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/hr_attendance_break_and_resume.png"],
    "category": "Human Resources",
    "depends": [
        "base",
        "hr",
        "hr_attendance",
    ],
    "data": [      
        "security/ir.model.access.csv",    
        "views/res_config_settings.xml",
        "views/hr_attendance_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/hr_attendance_break_and_resume/static/src/js/attendance_menu.js",
            "/hr_attendance_break_and_resume/static/src/js/attendance_menu.xml",
        ],
        "hr_attendance.assets_public_attendance":[
            "/hr_attendance_break_and_resume/static/src/js/public_kiosk_app.js",
            "/hr_attendance_break_and_resume/static/src/js/attendance_break_dialog.js",
            "/hr_attendance_break_and_resume/static/src/js/attendance_break_dialog.xml",
        ]
    },     
    "installable": True,
    "application": True,
    "price"                 :  35,
    "currency"              :  "EUR",
}