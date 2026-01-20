from odoo import models, api, _
from datetime import datetime,timedelta

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def check_attendance_and_notify(self):

        def get_ordinal_suffix(day):
            if 10 <= day % 100 <= 20:  # Handle special case for teens
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            return suffix

        # Function to format date
        def format_date_with_suffix(date_obj):
            day = date_obj.day
            suffix = get_ordinal_suffix(day)
            return date_obj.strftime(f"%-d{suffix} %b, %Y")
        
        # Function to extract hour and minute
        def parse_hour_minute(time_str):
            # Split the time string at the decimal point
            if '.' in time_str:
                hour, fraction = time_str.split('.')
                hour = int(hour)
                minute = int(float(f'0.{fraction}') * 60)  # Convert fraction to minutes
            else:
                hour = int(time_str)
                minute = 0
            return hour, minute
        
        today = datetime.now().date()
        today1 = datetime.now()

        employees = self.env['hr.employee'].search([])

        for employee in employees:
            if employee.contract_id:
                if employee.contract_id.state == 'open':

                    group_system = self.env.ref("base.group_system")
                    users_with_admin_settings = self.env["res.users"].search(
                    [("groups_id", "in", group_system.id)]
                    )
                
                    if employee.user_id in users_with_admin_settings or employee.exp_employee:
                        continue

                    unpaid_leave_type = self.env['hr.leave.type'].search([('leave_type', '=', 'unpaid')], limit=1)
                    unpaid_leave_allocation = self.env['hr.leave.allocation'].search([
                        ('employee_id', '=', employee.id),
                        ('holiday_status_id', '=', unpaid_leave_type.id),
                        ('state', '=', 'validate')
                    ], limit=1)

                    # Calculate total working hours and find gaps
                    missing_hours = self.attendance_difference(today, employee)
                    check_in_time = employee.resource_calendar_id.attendance_ids.filtered(lambda r: r.day_period == 'morning' and r.dayofweek == str(today.weekday())).hour_from
                    check_in_time = int(check_in_time) if check_in_time.is_integer() else (round(check_in_time * 2))/2
    
                    leave = self.search([
                        ('employee_id', '=', employee.id),
                        ('date_from', '<=', today),
                        ('date_to', '>=', today),
                    ], limit=1)

                    already_leave = False
                    new_leave_info = {
                            'employee_id': employee.id,
                            'holiday_status_id' : unpaid_leave_type.id,
                            'holiday_allocation_id': unpaid_leave_allocation.id,
                            'request_date_from': today,
                            'request_date_to': today,
                            'request_unit_hours': True,
                            'request_unit_half': False,
                        }
                    
                    if leave:
                        missing_hours -= leave.number_of_hours_display 
                        already_leave = True

                        if missing_hours >= 0.5:

                            leave_created = False
                            
                            # Half Day Leave Type
                            if leave.request_unit_half:

                                if leave.request_date_from_period == 'am':
                                    start_datetime = today1.replace(hour=14, minute=30, second=0, microsecond=0) #2:30 IST
                                    time_to_add = timedelta(hours=missing_hours)
                                    end_datetime = start_datetime + time_to_add

                                    new_leave_info.update({
                                    'name': f'Auto Leave created of {round(missing_hours * 2) / 2} hours on {format_date_with_suffix(today)}.',
                                    'request_date_from': start_datetime - timedelta(hours=5, minutes=30),
                                    'request_date_to': end_datetime - timedelta(hours=5, minutes=30),
                                    'date_from': start_datetime - timedelta(hours=5, minutes=30),
                                    'date_to': end_datetime - timedelta(hours=5, minutes=30),
                                    'request_hour_from': '14.5',
                                    'request_hour_to': f'{int(14.5 + round(missing_hours * 2) / 2) if (14.5 + round(missing_hours * 2) / 2).is_integer() else 14.5 + round(missing_hours * 2) / 2}',
                                    })

                                else: 
                                    hr = int(check_in_time)
                                    mint = (check_in_time - int(check_in_time))*60
                                    start_datetime = today1.replace(hour=hr, minute=mint, second=0, microsecond=0)
                                    time_to_add = timedelta(hours=missing_hours)
                                    end_datetime = start_datetime + time_to_add

                                    new_leave_info.update({
                                    'name': f'Auto Leave created of {round(missing_hours * 2) / 2} hours on {format_date_with_suffix(today)}.',
                                    'date_from': start_datetime - timedelta(hours=5, minutes=30),
                                    'date_to': end_datetime - timedelta(hours=5, minutes=30),
                                    'request_date_from': start_datetime - timedelta(hours=5, minutes=30),
                                    'request_date_to': end_datetime - timedelta(hours=5, minutes=30),
                                    'request_hour_from': str(check_in_time),
                                    'request_hour_to': f'{int(check_in_time + round(missing_hours * 2) / 2) if (check_in_time + round(missing_hours * 2) / 2).is_integer() else check_in_time + round(missing_hours * 2) / 2}',
                                    })

                            # custom hours leave type
                            elif leave.request_unit_hours:
                                hour, minute = parse_hour_minute(leave.request_hour_to)
                                start_datetime = today1.replace(hour=hour, minute=minute, second=0)
                                time_to_add = timedelta(hours=missing_hours)
                                end_datetime = start_datetime + time_to_add

                                new_leave_info.update({
                                    'name': f'Auto Leave created of {round(missing_hours * 2) / 2} hours on {format_date_with_suffix(today)}.',
                                    'date_from': start_datetime - timedelta(hours=5, minutes=30),
                                    'date_to': end_datetime - timedelta(hours=5, minutes=30),
                                    'request_date_from': start_datetime - timedelta(hours=5, minutes=30),
                                    'request_date_to': end_datetime - timedelta(hours=5, minutes=30),
                                    'request_hour_from': leave.request_hour_to,
                                    'request_hour_to': f'{int(float(leave.request_hour_to) + round(missing_hours * 2) / 2) if (float(leave.request_hour_to) + round(missing_hours * 2) / 2).is_integer() else float(leave.request_hour_to) + round(missing_hours * 2) / 2}',
                                    'number_of_hours_display' : missing_hours
                                    })

                            leave_created = super(HrLeave, self).create(new_leave_info)

                            if leave_created:
                                self.env['bus.bus']._sendone(
                                employee.user_id.partner_id, 'cr_notification_auto_leave', 
                                {'title': _('Leave Notification'),
                                'message': 'Your Leave has been created. Click here to view.',
                                'leave_id': leave_created.id})
                    
                    elif missing_hours >= 0.5 and not already_leave:

                        if missing_hours > 3.5:
                            new_leave_info.update( {
                                'name': f'Auto leave created of {round(missing_hours * 2) / 2} hours on {format_date_with_suffix(today)}.',
                                'request_hour_from': str(check_in_time),
                                'request_hour_to': f'{int(check_in_time + round((missing_hours+1) * 2) / 2) if (check_in_time + round((missing_hours+1) * 2) / 2).is_integer() else check_in_time + round((missing_hours+1) * 2) / 2}',
                                'number_of_hours_display' : missing_hours
                            })
                        else:
                            new_leave_info.update( {
                                'name': f'Auto leave created of {round(missing_hours * 2) / 2} hours on {format_date_with_suffix(today)}.',
                                'request_hour_from': str(check_in_time),
                                'request_hour_to': f'{int(check_in_time + round(missing_hours * 2) / 2) if (check_in_time + round(missing_hours * 2) / 2).is_integer() else check_in_time + round(missing_hours * 2) / 2}',
                                'number_of_hours_display' : missing_hours
                            })
                        res = super(HrLeave, self).create(new_leave_info)
                        res.write(new_leave_info)

                        if res:
                            self.env['bus.bus']._sendone(
                                employee.user_id.partner_id, 'cr_notification_auto_leave', 
                                {'title': _('Leave Notification'),
                                    'message': 'Your Unpaid Leave has been created. Click here to view.',
                                    'leave_id': res.id
                                }
                            )

                    elif missing_hours > 0.1667 and missing_hours < 0.5:
                        missing_minutes = round(missing_hours * 60)

                        group_system = self.env.ref("base.group_system")
                        users_with_admin_settings = self.env["res.users"].search(
                            [("groups_id", "in", group_system.id)]
                        )

                        for user in users_with_admin_settings:
                            message = {
                                    "title": f"{employee.name}'s Attendance Alert",
                                    "type": "danger",
                                    "message": f"{missing_minutes} minutes missed!",
                                    "sticky": True,
                            }
                            self.env["bus.bus"]._sendone(
                                user.partner_id,
                                "simple_notification",
                                message,
                            )

                        email_values = {
                            'subject': _('Attendance Alert: Missed Time Today'),
                            'email_to': employee.work_email,  # Employee's email
                            'body_html': f"""
                                <p>Dear {employee.name},</p>
                                <p>This is to inform you that <strong>{missing_minutes} minutes</strong> of your today's schedule were missed.</p>
                                <p>Please ensure you adhere to your schedule in the future.</p>
                                <br/>
                                <p>Thank you,<br/>HR Team<br/>Creyox Technologies</p>
                            """,
                            'email_from': self.env.user.email or 'info@creyox.com',
                        }
                        
                        mail = self.env['mail.mail'].create(email_values)
                        mail.send()
                        
                    # checking out in case user forgot to checkout
                    attendance = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', datetime.combine(today, datetime.min.time())),
                    ('check_out', '=', False)
                    ])
                    
                    if attendance:
                        attendance.write({'check_out' : attendance.check_in })

    def attendance_difference(self, today, employee):
        """Check if the attendance for the day is valid based on working hours."""
        attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', datetime.combine(today, datetime.min.time())),
                ('check_out', '<=', datetime.combine(today, datetime.max.time()))
            ])
        
        working_days = []
        for slot in employee.resource_calendar_id.attendance_ids:
            if int(slot.dayofweek) not in working_days:
                working_days.append(int(slot.dayofweek))

        
        public_holidays  = self.env['resource.calendar.leaves'].search([('resource_id', '=', False)])
        today1 = datetime.now()

        for holiday in public_holidays:             #checks if its public holiday
            if today1 >= holiday.date_from and today1 <= holiday.date_to:
                return 0
            
        if not today.weekday() in working_days:     #checks if its working day
            return 0                            

        else:   
            total_working_hours_of_today = sum([a.worked_hours for a in attendances])
            required_hours = 0
            for slot in employee.resource_calendar_id.attendance_ids:
                if int(slot.dayofweek) == today.weekday():
                    required_hours += (slot.hour_to - slot.hour_from) 
            missing_hours = required_hours - total_working_hours_of_today
            return missing_hours


