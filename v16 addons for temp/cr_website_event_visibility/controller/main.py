# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import http
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController  # Import base controller

class WebsiteEventControllerInherit(WebsiteEventController):

    @http.route(['''/event/<model("event.event"):event>/register'''], type='http', auth="public", website=True, sitemap=False)
    def event_register(self, event, **post):
        if event.website_visibility == 'logged_users' and request.env.user._is_public():
            return request.redirect('/web/login?redirect=%s' % request.httprequest.url)

        # Call the original method using super()
        values = super().event_register(event, **post)
        return values
