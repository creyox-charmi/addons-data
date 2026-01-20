# -*- coding: utf-8 -*-
from odoo import models, fields

class Partner(models.Model):
    _inherit = 'res.partner'

    # Campos para redes sociales
    facebook_url = fields.Char(string='Facebook')
    instagram_url = fields.Char(string='Instagram')
    linkedin_url = fields.Char(string='LinkedIn')
    twitter_url = fields.Char(string='X')
    youtube_url = fields.Char(string='YouTube')
    github_url = fields.Char(string='GitHub')