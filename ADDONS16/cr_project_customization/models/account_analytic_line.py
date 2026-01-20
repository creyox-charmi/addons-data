# -*- coding: utf-8 -*-
# Part of Creyox technologies.

from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools import float_compare


class TimeSheet(models.Model):
    _inherit = "account.analytic.line"

    task_type = fields.Selection([("r_and_d", "R & D"),("development", "Development"), ("qa", 'QA'), ("configuration", 'Configuration')], string="Task Type")


