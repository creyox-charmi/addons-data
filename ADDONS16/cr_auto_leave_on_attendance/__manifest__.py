{
    "name": "Auto Leave Generation",
    "author": "Creyox Technologies",
    "version": "16.0.0.0",
    "summary": "Generates auto unpaid leave when attendance doesn't match the daily requirement or its less than the leave",
    "sequence": 9,
    "description": """Generates auto unpaid leave when attendance doesn't match the daily requirement or its less than the leave""",
    "category": "",
    "website": "",
    "depends": ["base", "hr_holidays", 'hr', 'hr_attendance', 'bus', "cr_hr_attendance_late_reasoning" ],
    "data": [
        'data/schedule_action.xml',
    ],
    "demo": [],
    'assets': {
        'web.assets_backend': [
            'cr_auto_leave_on_attendance/static/src/js/notification_click.js',
        ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
