from odoo import fields, models, api

class LoginPlatform(models.Model):
    _name = 'cr.login.platform'

    name  = fields.Char(string = 'Login Platform')