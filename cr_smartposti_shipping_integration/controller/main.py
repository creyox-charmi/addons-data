# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class SmartPostiController(http.Controller):
    @http.route(
        "/shop/smartposti/set_service_type", type="json", auth="public", website=True
    )
    def set_service_type(self, service_type="pudo", **kwargs):
        """Store selected service type in session"""
        request.session["smartposti_service_type"] = service_type

        order = request.website.sale_get_order()
        if order:
            order.sudo().write({"smartposti_service_type": service_type})

        return {"success": True}

    @http.route("/shop/smartposti/set_place", type="json", auth="public", website=True)
    def set_place(self, place_id=None, **kwargs):
        """Store selected pickup place in order"""
        order = request.website.sale_get_order()

        if order and place_id:
            place = request.env["smartposti.place"].sudo().browse(int(place_id))
            if place.exists():
                order.sudo().write({"smartposti_place_id": place.id})
                return {"success": True, "place_name": place.name}

        return {"success": False}


