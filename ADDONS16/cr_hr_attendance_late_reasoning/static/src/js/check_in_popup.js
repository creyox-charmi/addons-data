odoo.define('cr_hr_attendance_late_reasoning.check_in_popup', function (require) {
    "use strict";

    var MyAttendance = require('hr_attendance.my_attendances');
    var core = require('web.core');
    const session = require('web.session');

    MyAttendance.include({
        update_attendance: function () {
            var self = this;

            // Check if the user is late
            this._rpc({
                model: 'hr.employee',
                method: 'is_checked_in_late',
                args: [self.employee.id],
                context: session.user_context,
            }).then(function (result) {
            
                if (result) {
                    // Late check-in popup logic
                    if (result == 'limit over') {
                        
                        document.getElementById('limit_over_popup').style.display = "block";
                        document.getElementById("okay_btn").addEventListener("click", function () {
                            document.getElementById('limit_over_popup').style.display = "none";
                        });
                    } else {

                        document.getElementById('late_checkin_popup').style.display = "block";
                        document.getElementById("okay_button").addEventListener("click", function () {
                            let rzn = document.getElementById('reason_input').value;
                            if (!rzn || rzn.trim() === '' || rzn.trim() === '-') {
                                alert("Please enter a reason.");
                            } else {
                                document.getElementById("late_checkin_popup").style.display = "none";

                                // Mark attendance and assign late reason
                                self._rpc({
                                    model: 'hr.employee',
                                    method: 'attendance_manual',
                                    args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
                                    context: session.user_context,
                                }).then(function (result) {
                                    if (result.action) {
                                        self._rpc({
                                            model: 'hr.attendance',
                                            method: 'late_reason_assigning',
                                            args: [result.action.attendance.id, rzn],
                                            context: session.user_context,
                                        });
                                        // Always show remainder popup
                                        self.do_action(result.action);
                                        alert('Don\'t forget to Start/Resume your respective task.');
                                    } else if (result.warning) {
                                        self.displayNotification({ title: result.warning, type: 'danger' });
                                    }
                                });
                            }
                        });
                    }
                } else {
                    self._rpc({
                        model: 'hr.employee',
                        method: 'attendance_manual',
                        args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
                        context: session.user_context,
                    })
                        .then(function (result) {
                            if (result.action) {
                                self.do_action(result.action);
                            } else if (result.warning) {
                                self.displayNotification({ title: result.warning, type: 'danger' });
                            }
                        });
                }
            });
        },
    });
});
