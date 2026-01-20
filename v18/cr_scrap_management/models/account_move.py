from odoo import api, Command, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError


class Account(models.Model):
    _inherit = 'account.move'