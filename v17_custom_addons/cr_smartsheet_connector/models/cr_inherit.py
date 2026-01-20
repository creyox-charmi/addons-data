# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import json
from odoo import models, fields, _, api
from odoo.http import request, Response


class Contacts(models.Model):
    _inherit = 'res.partner'

    cr_smart_sheet_id=fields.Char('SmartSheet Id')

class Users(models.Model):
    _inherit='res.users'

    cr_smartsheet_user_id=fields.Char('SmartSheet User Id')
