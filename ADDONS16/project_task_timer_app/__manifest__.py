# -*- coding: utf-8 -*-

{
    'name': 'Project Task Timer with Start/Stop/Pause',
    "author": "Edge Technologies",
    'version': '16.0.1.1',
    'live_test_url': "https://youtu.be/QLU-cdefQcg",
    "images":['static/description/main_screenshot.png'],
    'summary': "Project task timer task timesheet generated based timer timesheet timer project timesheet timer watch on task start stop timer project timer project start stop timer start project task timer start task timer duration of task task start stop functionality",
    'description': """This app is created to add a timer to each task. project task timer can be started and ended by the assigned person of the task and based on that, timesheet entry is generated.
    

timer start
project start task start and stop timer of task
project track time
task track time
track task time 
project start stop timer 
project task subtask checklist
timer watch on task
task start stop timer
project timer
project start stop timer
start project task timer
start task timer duration of task
start stop timer task 
start stop task timer duration of task
project timer
tasks timer task using start pause stop buttons
project tasks timer
project tasks duration project tasks start stop functionality
tasks duration
start and stop task
start and stop the timer

project task timer with start/stop/pause
task timer
task start-stop-pause buttons
project task start stop


    """,
    "license" : "OPL-1",
    'depends': ['base','portal','project','hr_timesheet','analytic'],
    'data': [
        'security/ir.model.access.csv',
        'views/main_project_start_view.xml',
            ],
    'installable': True,
    'auto_install': False,
    'price': 8,
    'currency': "EUR",
    'category': 'Projects',
    'assets': {
        'web.assets_backend': [
            'project_task_timer_app/static/src/css/add_color.css',
            'project_task_timer_app/static/src/js/timer.js',
            'project_task_timer_app/static/src/xml/timer.xml',
        ],    
    },

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
