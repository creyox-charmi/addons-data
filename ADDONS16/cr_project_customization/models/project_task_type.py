# -*- coding: utf-8 -*-
# Part of Creyox technologies.

from odoo import models, fields, api

class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    is_paid = fields.Boolean(string="Is Paid?")