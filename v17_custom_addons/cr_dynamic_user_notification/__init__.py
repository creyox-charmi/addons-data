# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID, _
from . import models

def _user_notify_uninstall_hook(env):
    """This method archives user notify automated actions at uninstall of module"""
    #env = api.Environment(cr, SUPERUSER_ID, {})
    automated_action_ids = env['base.automation'].search([('is_notify_action', '=', True)])
    if automated_action_ids:
        #automated_action_ids.sudo().write({'active': False})
        automated_action_ids.sudo().unlink()
