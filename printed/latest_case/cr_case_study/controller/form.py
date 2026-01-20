# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import base64
import json
import imghdr
from odoo import http
from odoo.http import request
from odoo.tools import sql
from odoo.addons.website.controllers.form import WebsiteForm

class WebsiteSaleForm(WebsiteForm):

    @http.route('/website/form/crm.lead', type='http', auth="public", methods=['POST'], website=True)
    def website_form_saleorder(self, **kwargs):
        print()

