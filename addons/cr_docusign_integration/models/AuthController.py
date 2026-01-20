# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import http
from odoo.http import request
import urllib.parse
from werkzeug.utils import redirect


class DocusignAuthController(http.Controller):

    @http.route('/docusign/auth/callback', type='http', auth='public')
    def dynamic_callback_handler(self, **kwargs):
        full_url = request.httprequest.url
        parsed_url = urllib.parse.urlparse(full_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        code = query_params.get('code', [None])[0]

        if code:
            user = request.env.user
            if hasattr(user, 'handle_authorization_code'):
                user.handle_authorization_code(code)
            return request.render('cr_docusign_integration.success_redirect_template')

        # fallback
        return redirect('/web')


