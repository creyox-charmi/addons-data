# -*- coding: utf-8 -*-
from odoo import models, fields, _


class BaseAutomation(models.Model):
    _inherit = 'base.automation'

    is_notify_action = fields.Boolean()
