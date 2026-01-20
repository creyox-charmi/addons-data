# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from . import models
from datetime import datetime, timedelta
import pytz


def post_init_hook(env):
    """Set cron to run at 11 PM Israel time (21:00 UTC)"""
    israel_tz = pytz.timezone('Asia/Jerusalem')
    utc_tz = pytz.UTC

    now_utc = datetime.now(utc_tz)
    now_israel = now_utc.astimezone(israel_tz)

    next_run_israel = now_israel.replace(hour=23, minute=0, second=0, microsecond=0)

    if now_israel.hour >= 23:
        next_run_israel += timedelta(days=1)

    next_run_utc = next_run_israel.astimezone(utc_tz)

    cron = env.ref('cr_daily_opportunity_report.ir_cron_send_daily_opportunity_report', raise_if_not_found=False)
    if cron:
        cron.write({
            'nextcall': next_run_utc.replace(tzinfo=None),
        })