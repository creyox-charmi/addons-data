{
    "name": "Attendance Customization",
    "author": "Creyox Technologies",
    "version": "16.0.0.0",
    "summary": "",
    "sequence": 10,
    "description": """""",
    "category": "",
    "website": "",
    "depends": ["base", "hr", "hr_attendance", "cr_employee_customisation"],
    "data": [
        "security/ir.model.access.csv",
        "views/resource_calendar_form.xml",
        "views/hr_attendance_tree.xml",
        "views/hr_employee.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "assets": {
        "web.assets_backend": [
            "cr_hr_attendance_late_reasoning/static/src/xml/popup.xml",
            "cr_hr_attendance_late_reasoning/static/src/xml/check-In-disable.xml",
            "cr_hr_attendance_late_reasoning/static/src/js/check_in_popup.js",
        ],
    },
    "license": "LGPL-3",
}
