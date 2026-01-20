# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug
from werkzeug.urls import url_encode

from odoo import http, tools, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.addons.base_setup.controllers.main import BaseSetup
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)

LOGIN_SUCCESSFUL_PARAMS.add('account_created')


class SubAuthSignupHome(AuthSignupHome):

    @http.route()
    def web_login(self, *args, **kw):
        print("CUSTOMMMMMMMMMMMMMMM")
        dic = {'disable_database_manager': False, 'signup_enabled': True, 'reset_password_enabled': True}
        qcontext = self.get_auth_signup_qcontext()
        print(qcontext)
        if qcontext == dic:
            print("!!!!!!!!!!!!!1")
            print('true')
            print("!!!!!!!!!11")
        res = super(SubAuthSignupHome,self).web_login( *args, **kw)
        return res