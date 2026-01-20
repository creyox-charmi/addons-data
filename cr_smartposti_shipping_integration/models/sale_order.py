# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # NEW: Store selected service type
    smartposti_service_type = fields.Selection(
        [("pudo", "Parcel Machines"), ("courier", "Courier")],
        string="SmartPosti Service Type",
        copy=False,
    )

    # NEW: Store selected place
    smartposti_place_id = fields.Many2one(
        "smartposti.place", string="Selected Pickup Point", copy=False
    )

    def _action_confirm(self):
        """Override to transfer SmartPosti data to picking"""
        result = super(SaleOrder, self)._action_confirm()

        # Transfer SmartPosti data to pickings
        for order in self:
            if order.carrier_id and order.carrier_id.delivery_type == "smartposti":
                pickings = order.picking_ids.filtered(
                    lambda p: p.picking_type_code == "outgoing"
                    and not p.smartposti_place_id
                )

                if pickings and order.smartposti_place_id:
                    pickings.write(
                        {"smartposti_place_id": order.smartposti_place_id.id}
                    )

        return result

    @api.depends(
        "order_line.price_total",
        "order_line.price_subtotal",
        "carrier_id",
        "partner_id.country_id",
    )
    def _compute_amount_delivery(self):
        """Override to handle SmartPosti dynamic pricing"""

        super(SaleOrder, self)._compute_amount_delivery()

        for order in self.filtered(lambda o: o.website_id and o.carrier_id):
            if order.carrier_id.delivery_type == "smartposti":

                partner_country = order.partner_id.country_id
                if not partner_country:
                    continue

                places_exist = self.env["smartposti.place"].search_count(
                    [("country", "=", partner_country.code), ("active", "=", True)],
                    limit=1,
                )

                if not places_exist:
                    continue

                service_type = order.smartposti_service_type or "pudo"
                if request and hasattr(request, "session"):
                    service_type = request.session.get(
                        "smartposti_service_type", service_type
                    )
                    if service_type != order.smartposti_service_type:
                        order.smartposti_service_type = service_type

                company = order.company_id

                country_price = self.env["smartposti.country.price"].search(
                    [
                        ("company_id", "=", company.id),
                        ("service_type", "=", service_type),
                        ("country_id", "=", partner_country.id),
                    ],
                    limit=1,
                )

                if country_price:
                    target_price = country_price.price
                else:
                    if service_type == "courier":
                        target_price = company.smartposti_courier_price or 0.00
                    else:
                        target_price = company.smartposti_pudo_price or 0.00

                # target_price = order.carrier_id._calculate_price_with_tax(target_price, order)

                delivery_lines = order.order_line.filtered("is_delivery")
                if delivery_lines:
                    for line in delivery_lines:
                        if line.price_unit != target_price:
                            line.write({"price_unit": target_price})

                        # ADD THIS: Update description with place name
                        if order.smartposti_place_id and service_type == "pudo":
                            place = order.smartposti_place_id
                            new_description = f"Smartposti \nPickup Point: {place.name}\nAddress: {place.address}, {place.city}"
                            if line.name != new_description:
                                line.write({"name": new_description})

                    if (
                        order.website_id.show_line_subtotals_tax_selection
                        == "tax_excluded"
                    ):
                        order.amount_delivery = sum(
                            delivery_lines.mapped("price_subtotal")
                        )
                    else:
                        order.amount_delivery = sum(
                            delivery_lines.mapped("price_total")
                        )
