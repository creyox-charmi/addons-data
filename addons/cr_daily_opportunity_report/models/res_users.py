# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api
from datetime import datetime, timedelta
import pytz

CR_CRM_FIELDS = ['receive_daily_opportunity_report']


class ResUsers(models.Model):
    _inherit = 'res.users'

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + CR_CRM_FIELDS

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + CR_CRM_FIELDS


    receive_daily_opportunity_report = fields.Boolean(
        string='Receive Daily Opportunity Report',
        default=False,
        compute='_compute_receive_daily_opportunity_report',
        store=True,
        readonly=False,
    )

    @api.depends('groups_id')
    def _compute_receive_daily_opportunity_report(self):
        system_group = self.env.ref('base.group_system', raise_if_not_found=False)
        erp_manager_group = self.env.ref('base.group_erp_manager', raise_if_not_found=False)

        for user in self:
            user.receive_daily_opportunity_report = False  # always reset

            if (
                    (system_group and system_group in user.groups_id) or
                    (erp_manager_group and erp_manager_group in user.groups_id)
            ):
                user.receive_daily_opportunity_report = True

    @api.model
    def _send_daily_opportunity_report(self):
        """Cron job method to send daily opportunity reports"""
        current_utc_time = datetime.utcnow()

        all_users = self.env['res.users'].search([
            ('active', '=', True),
            ('share', '=', False)
        ])

        users_to_notify = []

        for user in all_users:
            user_tz_name = user.tz or 'UTC'

            try:
                user_tz = pytz.timezone(user_tz_name)
                user_time = current_utc_time.replace(tzinfo=pytz.UTC).astimezone(user_tz)

                if user.receive_daily_opportunity_report:
                    users_to_notify.append(user)

            except Exception:
                continue

        for user in users_to_notify:
            self._send_report_to_user(user)

    def _send_report_to_user(self, user):
        """Send the daily report to a specific user"""
        user_tz_name = user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz_name)

        current_utc = datetime.utcnow().replace(tzinfo=pytz.UTC)
        user_now = current_utc.astimezone(user_tz)

        start_of_day = user_now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = user_now.replace(hour=23, minute=59, second=59, microsecond=999999)

        start_of_day_utc = start_of_day.astimezone(pytz.UTC).replace(tzinfo=None)
        end_of_day_utc = end_of_day.astimezone(pytz.UTC).replace(tzinfo=None)

        won_opportunities = self.env['crm.lead'].search([
            ('probability', '=', 100),
            ('date_closed', '>=', start_of_day_utc),
            ('date_closed', '<=', end_of_day_utc),
        ])

        lost_opportunities = self.env['crm.lead'].with_context(active_test=False).search([
            ('probability', '=', 0),
            ('date_closed', '>=', start_of_day_utc),
            ('date_closed', '<=', end_of_day_utc),
        ])

        if not won_opportunities and not lost_opportunities:
            return

        template = self.env.ref('cr_daily_opportunity_report.email_template_daily_opportunity_report',
                                raise_if_not_found=False)

        if template:
            ctx = {
                'won_opportunities': won_opportunities,
                'lost_opportunities': lost_opportunities,
                'user_date': user_now.strftime('%Y-%m-%d'),
            }

            template.with_context(**ctx).send_mail(user.id, force_send=True, email_values={
                'email_to': user.email,
            })
