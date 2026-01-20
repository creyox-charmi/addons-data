# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import http
from odoo.http import request, Response
import json

class SmartsheetController(http.Controller):

    @http.route('/smartsheet/Auth/callback', type='http', auth='public')
    def smartsheet_callback(self, **kwargs):
        authorization_code = kwargs.get('code')
        print('called')
        print('authorization_code')
        print(authorization_code)

        record_id = request.session.get("smartsheet_Record_id")

        if not record_id:
            return Response("Record ID not found", status=400)

        # Fetch the Smartsheet configuration record
        config = request.env['cr.smartsheet.config'].sudo().browse(int(record_id))
        if not config.exists():
            return  Response("No Smartsheet configuration found.",status=404)

        # Exchange the authorization code for tokens
        try:
            result = config.exchange_code_for_token(authorization_code,config.id)
            return result
        except Exception as e:
            return f"Error: {str(e)}"