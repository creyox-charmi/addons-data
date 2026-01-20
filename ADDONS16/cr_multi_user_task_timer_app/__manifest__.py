# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Multi-User Project Task Timer App Advance Task Timer  | Set Timer For Task | Task Time Tracking",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Project",
    "summary": """
       This module significantly enhances the standard Odoo project management features by introducing personal 
       task timers for users. With real-time tracking, precise time logging, and detailed timesheet generation, 
       it provides a robust solution for managing time in collaborative environments. Each user’s work is tracked 
       individually, making the system highly scalable for projects with multiple contributors.

       Additionally, at the end of a task, users are prompted to enter descriptions for their timesheets,
        which automatically log the time spent on each task.The timers sync with the backend in real-time, 
        ensuring that even if the page is closed or a user switches tasks, their timer data remains consistent.

        Project Task Time Tracker Pro
        Multi-User Task Timer
        Advanced Task Timer for Projects
        Personal Timer for Task Management
        Collaborative Task Time Logger
        Team Task Time Tracker
        Odoo Project Timer
        Task Time Tracking Plus
        Smart Task Timer
        Project Time Management Tool
        User-Based Task Timer
        Project Timer for Teams
        Task Timer with Timesheets
        Efficient Task Time Tracker
        Real-Time Task Timer
        Advanced Project Task Timer
        Task Work Timer Pro
        Accurate Task Time Logger
        Project Timekeeper for Odoo
        Task Duration Tracker Pro
        How to track time on tasks in Odoo?
        What is the best project timer for Odoo?
        Can I manage personal task timers in Odoo?
        How do I log time spent on tasks in Odoo?
        What are the features of Odoo task time tracking tools?
        How to generate timesheets in Odoo?
        Is there a multi-user task timer for Odoo?
        How to use a collaborative task time logger in Odoo?
        What is the best time tracking app for Odoo projects?
        How does the Odoo project timer work?
        Can I sync task timers in real-time with Odoo?
        How to track multiple contributors' time in Odoo?
        What are the advantages of using a personal task timer in Odoo?
        How to automatically log time for tasks in Odoo?
        Can I track project durations effectively in Odoo?
        What is a smart task timer for Odoo projects?
        How do I implement a project time management tool in Odoo?
        What features should I look for in an Odoo task timer?
        How to set up a task timer with timesheets in Odoo?
        Are there any efficient task time trackers for Odoo?
        How to set up a project task timer in Odoo?
        Can Odoo track time for multiple users on a single project?
        How to create a timesheet entry in Odoo for project tasks?
        What is the best way to manage task timers in Odoo?
        How to stop and resume task timers in Odoo?
        Can I link task timers to specific employees in Odoo?
        How to customize the timesheet description wizard in Odoo?
        What are the benefits of using a task timer in Odoo for project management?
        How to handle multiple task timers for different users in Odoo?
        What happens if a user forgets to stop the task timer in Odoo?
        How to generate reports based on task timers in Odoo?
        Is there a way to pause task timers in Odoo?
        How to integrate task timers with project management in Odoo?
        What are the required fields for creating a timesheet in Odoo?
        Can I automate task timer entries in Odoo?
        How to troubleshoot issues with task timers in Odoo?
        What user roles are needed to manage task timers in Odoo?
        How to reset task timers in Odoo?
        Are there any third-party apps for managing task timers in Odoo?
        How to ensure accurate time tracking for project tasks in Odoo?

    """,
    "license": "LGPL-3",
    "version": "16.0.0.1",
    "sequence": 10,
    "description": """
       This module significantly enhances the standard Odoo project management features by introducing personal 
       task timers for users. With real-time tracking, precise time logging, and detailed timesheet generation, 
       it provides a robust solution for managing time in collaborative environments. Each user’s work is tracked 
       individually, making the system highly scalable for projects with multiple contributors.

       Additionally, at the end of a task, users are prompted to enter descriptions for their timesheets,
        which automatically log the time spent on each task.The timers sync with the backend in real-time, 
        ensuring that even if the page is closed or a user switches tasks, their timer data remains consistent.

        Project Task Time Tracker Pro
        Multi-User Task Timer
        Advanced Task Timer for Projects
        Personal Timer for Task Management
        Collaborative Task Time Logger
        Team Task Time Tracker
        Odoo Project Timer
        Task Time Tracking Plus
        Smart Task Timer
        Project Time Management Tool
        User-Based Task Timer
        Project Timer for Teams
        Task Timer with Timesheets
        Efficient Task Time Tracker
        Real-Time Task Timer
        Advanced Project Task Timer
        Task Work Timer Pro
        Accurate Task Time Logger
        Project Timekeeper for Odoo
        Task Duration Tracker Pro
        How to track time on tasks in Odoo?
        What is the best project timer for Odoo?
        Can I manage personal task timers in Odoo?
        How do I log time spent on tasks in Odoo?
        What are the features of Odoo task time tracking tools?
        How to generate timesheets in Odoo?
        Is there a multi-user task timer for Odoo?
        How to use a collaborative task time logger in Odoo?
        What is the best time tracking app for Odoo projects?
        How does the Odoo project timer work?
        Can I sync task timers in real-time with Odoo?
        How to track multiple contributors' time in Odoo?
        What are the advantages of using a personal task timer in Odoo?
        How to automatically log time for tasks in Odoo?
        Can I track project durations effectively in Odoo?
        What is a smart task timer for Odoo projects?
        How do I implement a project time management tool in Odoo?
        What features should I look for in an Odoo task timer?
        How to set up a task timer with timesheets in Odoo?
        Are there any efficient task time trackers for Odoo?
        Can Odoo track time for multiple users on a single project?
        How to create a timesheet entry in Odoo for project tasks?
        What is the best way to manage task timers in Odoo?
        How to stop and resume task timers in Odoo?
        Can I link task timers to specific employees in Odoo?
        How to customize the timesheet description wizard in Odoo?
        What are the benefits of using a task timer in Odoo for project management?
        How to handle multiple task timers for different users in Odoo?
        What happens if a user forgets to stop the task timer in Odoo?
        How to generate reports based on task timers in Odoo?
        Is there a way to pause task timers in Odoo?
        How to integrate task timers with project management in Odoo?
        What are the required fields for creating a timesheet in Odoo?
        Can I automate task timer entries in Odoo?
        How to troubleshoot issues with task timers in Odoo?
        What user roles are needed to manage task timers in Odoo?
        How to reset task timers in Odoo?
        Are there any third-party apps for managing task timers in Odoo?
        How to ensure accurate time tracking for project tasks in Odoo?


    """,
    "category": "Project",
    "website": "www.creyox.com",
    "depends": ["base", "project", "contacts", "hr", "hr_timesheet"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task_timer.xml",
        "wizard/timesheet_description.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cr_multi_user_task_timer_app/static/src/css/task_timer.css",
            "cr_multi_user_task_timer_app/static/src/js/task_timer.js",
            "cr_multi_user_task_timer_app/static/src/xml/**/*",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.gif"],
    "price" : 75,
    "currency" : 'USD'
}
