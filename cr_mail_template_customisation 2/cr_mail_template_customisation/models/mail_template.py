from odoo import models, fields, api
from datetime import datetime, timedelta


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    user_ids = fields.Many2many(
        'res.users',
        string='Recipients',
        help='Select users who will receive this email template'
    )
    frequency_type = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')
    ], string='Frequency Type', default='days')

    frequency_interval = fields.Integer(
        string='Interval Number',
        default=1,
        help='Repeat every x (minutes/hours/days/weeks/months)'
    )

    # Weekly configuration
    week_day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], string='Day of Week')

    execution_hour = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
        ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
        ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')
    ], string='Hour',default='12')

    execution_minute = fields.Selection([
        ('0', '00'), ('15', '15'), ('30', '30'), ('45', '45')
    ], string='Minute',default='0')

    execution_period = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM')
    ], string='Period',default='pm')

    month_day = fields.Date(
        string='Select Date',
        help='Select the date for monthly execution'
    )

    scheduled_action_id = fields.Many2one(
        'ir.cron',
        string='Scheduled Action',
        readonly=True,
        help='Auto-generated scheduled action for this template'
    )

    is_res_users_model = fields.Boolean(
        string="Model is res.users",
        compute="_compute_is_res_users_model",
        store=True,  # storing makes the value available reliably in the form view
    )

    @api.depends('model_id')
    def _compute_is_res_users_model(self):
        for rec in self:
            rec.is_res_users_model = bool(rec.model_id and rec.model_id.model == 'res.users')

    @api.model
    def _is_user_model(self):
        """Check if current template applies to res.users model"""
        self.ensure_one()
        return self.model_id and self.model_id.model == 'res.users'


    def _calculate_next_call(self):
        """Calculate next call datetime based on frequency and configuration"""
        self.ensure_one()

        # Get user's timezone
        user_tz = self.env.user.tz or 'UTC'

        # Convert 12-hour format to 24-hour format
        def convert_to_24h(hour, minute, period):
            hour = int(hour)
            minute = int(minute)
            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            return hour, minute

        # In _calculate_next_call method, for weeks section, hardcode 12 PM:

        if self.frequency_type == 'weeks' and self.week_day is not False:
            import pytz

            # Get timezone objects
            local_tz = pytz.timezone(user_tz)
            utc_tz = pytz.UTC

            # Get current time in UTC and convert to local
            now_utc = fields.Datetime.now()
            now_local = pytz.utc.localize(now_utc).astimezone(local_tz)

            current_weekday = now_local.weekday()
            target_weekday = int(self.week_day)
            days_ahead = target_weekday - current_weekday

            # Hardcode 12:00 PM for weeks
            hours, minutes = 12, 0

            # If target day is today or already passed this week, move to next week
            if days_ahead < 0:
                days_ahead += 7
            elif days_ahead == 0:
                # Same day - check if execution time already passed
                temp_next_call = now_local.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                if temp_next_call <= now_local:
                    days_ahead = 7

            # Calculate next date in local timezone
            next_date = now_local.date() + timedelta(days=days_ahead)
            next_call_naive = datetime.combine(next_date, datetime.min.time()).replace(hour=hours, minute=minutes)
            next_call_local = local_tz.localize(next_call_naive)

            # Convert to UTC for storage
            next_call_utc = next_call_local.astimezone(utc_tz)

            return next_call_utc.replace(tzinfo=None)


        # 3. Update _calculate_next_call method for months section

        elif self.frequency_type == 'months' and self.month_day:

            import pytz

            local_tz = pytz.timezone(user_tz)

            utc_tz = pytz.UTC

            now_utc = fields.Datetime.now()

            now_local = pytz.utc.localize(now_utc).astimezone(local_tz)

            # Get the selected date

            selected_date = fields.Date.from_string(self.month_day)

            # Set time to 12:00 PM (noon)

            hours, minutes = 12, 0

            # Check if selected date already passed

            if selected_date <= now_local.date():
                # Move to next month - add approximately 30 days and adjust

                next_month = selected_date + timedelta(days=32)

                selected_date = selected_date.replace(year=next_month.year, month=next_month.month)

            next_call_naive = datetime.combine(selected_date, datetime.min.time()).replace(hour=hours, minute=minutes)

            next_call_local = local_tz.localize(next_call_naive)

            next_call_utc = next_call_local.astimezone(utc_tz)

            return next_call_utc.replace(tzinfo=None)

        else:
            if self.execution_hour and self.execution_period and self.frequency_type == 'days':
                import pytz

                local_tz = pytz.timezone(user_tz)
                utc_tz = pytz.UTC

                now_utc = fields.Datetime.now()
                now_local = pytz.utc.localize(now_utc).astimezone(local_tz)

                hours, minutes = convert_to_24h(self.execution_hour, self.execution_minute or '0',
                                                self.execution_period)
                next_call_naive = now_local.replace(hour=hours, minute=minutes, second=0, microsecond=0)

                if next_call_naive <= now_local:
                    next_call_naive += timedelta(days=1)

                next_call_local = local_tz.localize(next_call_naive.replace(tzinfo=None))
                next_call_utc = next_call_local.astimezone(utc_tz)

                return next_call_utc.replace(tzinfo=None)
            else:
                return fields.Datetime.now()

    def _create_or_update_scheduled_action(self):
        """Create or update scheduled action for email template"""
        self.ensure_one()

        if not self._is_user_model() or not self.user_ids:
            # Delete scheduled action if exists
            if self.scheduled_action_id:
                self.scheduled_action_id.unlink()
                self.scheduled_action_id = False
            return

        # Calculate next call time
        nextcall = self._calculate_next_call()
        print('nextcall : ',nextcall)

        cron_vals = {
            'name': f'Email Template: {self.name}',
            'model_id': self.env.ref('mail.model_mail_template').id,
            'state': 'code',
            'code': f'model.browse({self.id}).send_scheduled_email()',
            'interval_number': self.frequency_interval or 1,
            'interval_type': self.frequency_type or 'days',
            'active': True,
            'nextcall': nextcall,
        }

        if self.scheduled_action_id:
            self.scheduled_action_id.write(cron_vals)
        else:
            cron = self.env['ir.cron'].create(cron_vals)
            self.scheduled_action_id = cron.id

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        for template in templates:
            template._create_or_update_scheduled_action()
        return templates

    # Update write method relevant_fields:
    def write(self, vals):
        res = super().write(vals)
        # Only update scheduled action if relevant fields changed
        relevant_fields = {'model_id', 'user_ids', 'frequency_type', 'frequency_interval',
                           'week_day', 'execution_hour', 'execution_minute', 'execution_period', 'month_day'}
        if any(field in vals for field in relevant_fields):
            for template in self:
                template._create_or_update_scheduled_action()
        return res

    def unlink(self):
        # Delete associated scheduled actions
        scheduled_actions = self.mapped('scheduled_action_id')
        res = super().unlink()
        scheduled_actions.unlink()
        return res

    def send_scheduled_email(self):
        """Send email to all selected users"""
        self.ensure_one()

        if not self.user_ids:
            return

        for user in self.user_ids:
            try:
                self.send_mail(user.id, force_send=True)
            except Exception as e:
                # Log error but continue with other users
                self.env['ir.logging'].sudo().create({
                    'name': 'mail.template',
                    'type': 'server',
                    'level': 'error',
                    'message': f'Failed to send email to user {user.name}: {str(e)}',
                    'path': 'mail.template',
                    'func': 'send_scheduled_email',
                    'line': '1',
                })
                continue