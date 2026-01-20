# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class DynamicsCrmController(http.Controller):

    @http.route('/dynamics/callback', type='http', auth='public', methods=['GET'], website=True)
    def dynamics_callback(self, code=None, state=None, **kwargs):
        """Handle the OAuth callback from Microsoft and redirect to the form view."""
        if not code or not state:
            _logger.error("Callback failed: No code or state provided.")
            return "Error: Missing code or state in callback."
        try:
            dynamics_crm = request.env['cr.dynamics.crm'].sudo()
            action = dynamics_crm.handle_callback(code, state)
            form_url = f"/web#id={state}&model=cr.dynamics.crm&view_type=form"
            _logger.info(f"Callback successful. Redirecting to: {form_url}")
            return http.redirect_with_hash(form_url)
        except Exception as e:
            _logger.error(f"Callback error: {str(e)}")
            return f"Error during callback: {str(e)}"