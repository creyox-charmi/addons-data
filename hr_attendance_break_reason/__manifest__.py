# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "HR Attendance Break Reason",
    "summary": "Add reason field to attendance breaks",
    "version": "17.0.0.0",
    "category": "Human Resources",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "depends": [
        "hr_attendance_break_and_resume",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_attendance_break_reason_views.xml",
        "views/hr_attendance_views.xml",
    ],
    "assets": {
        "hr_attendance.assets_public_attendance": [
            "hr_attendance_break_reason/static/src/js/public_kiosk_app.js",
            "hr_attendance_break_reason/static/src/js/attendance_break_dialog.js",
            "hr_attendance_break_reason/static/src/js/attendance_break_dialog.xml",
        ]
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}