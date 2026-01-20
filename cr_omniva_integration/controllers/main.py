# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class OmnivaController(http.Controller):
    @http.route(
        "/shop/omniva/set_delivery_channel", type="json", auth="public", website=True
    )
    def set_delivery_channel(self, delivery_channel="COURIER", **kwargs):
        """Store selected delivery channel"""
        request.session["omniva_delivery_channel"] = delivery_channel

        # Save to order
        order = request.website.sale_get_order()
        if order:
            order.sudo().write({"omniva_delivery_channel": delivery_channel})

        return {"success": True}

    @http.route("/shop/omniva/set_location", type="json", auth="public", website=True)
    def set_location(self, location_id=None, **kwargs):
        """Store selected location"""
        order = request.website.sale_get_order()

        if order and location_id:
            location = request.env["omniva.location"].sudo().browse(int(location_id))
            if location.exists():
                order.sudo().write({"omniva_location_id": location.id})
                return {"success": True, "location_name": location.name}

        return {"success": False}
