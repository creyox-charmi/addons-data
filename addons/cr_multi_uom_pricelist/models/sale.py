# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _
from odoo.fields import Datetime


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "product_uom", "product_id", "order_id.pricelist_id", "product_uom_qty"
    )
    def _compute_price_unit(self):
        for line in self:
            if line.order_id.pricelist_id:
                pricelist_item = line.order_id.pricelist_id.item_ids

                if pricelist_item:
                    if line.product_template_id.attribute_line_ids:
                        price = line.order_id.pricelist_id.item_ids.search(
                            [
                                ("product_id", "=", line.product_id.id),
                                ("pricelist_id", "=", line.order_id.pricelist_id.id),
                                ("uom_id", "=", line.product_uom.id),
                            ]
                        )
                    else:
                        price = line.order_id.pricelist_id.item_ids.search(
                            [
                                ("product_tmpl_id", "=", line.product_template_id.id),
                                ("pricelist_id", "=", line.order_id.pricelist_id.id),
                                ("uom_id", "=", line.product_uom.id),
                            ]
                        )
                    if price:
                        if len(price) == 1:
                            if price.fixed_price:
                                if line.product_uom_qty >= price.min_quantity:
                                    line.price_unit = price.fixed_price
                                else:
                                    if line.product_id:
                                        # Get the UOM ratio to adjust the price based on the UOM
                                        uom_ratio = line.product_uom._compute_quantity(
                                            1, line.product_id.uom_id
                                        )

                                        # Get the currency of the pricelist, if it exists
                                        pricelist_currency = (
                                            line.order_id.pricelist_id.currency_id
                                            if line.order_id.pricelist_id
                                            else line.env.company.currency_id
                                        )

                                        # Convert the list price to the appropriate currency if the pricelist currency is different
                                        if (
                                            pricelist_currency
                                            != line.env.company.currency_id
                                        ):
                                            converted_price = (
                                                line.product_id.list_price
                                                * line.env.company.currency_id._get_conversion_rate(
                                                    line.env.company.currency_id,
                                                    pricelist_currency,
                                                )
                                            )
                                        else:
                                            converted_price = line.product_id.list_price

                                        # Adjust the price_unit based on UOM and the potential currency conversion
                                        line.price_unit = converted_price * uom_ratio

                                        # Set the discount to 0 since no pricelist item exists
                                        line.discount = 0

                            else:
                                if line.product_id:
                                    # Get the UOM ratio to adjust the price based on the UOM
                                    uom_ratio = line.product_uom._compute_quantity(
                                        1, line.product_id.uom_id
                                    )

                                    # Get the currency of the pricelist, if it exists
                                    pricelist_currency = (
                                        line.order_id.pricelist_id.currency_id
                                        if line.order_id.pricelist_id
                                        else line.env.company.currency_id
                                    )

                                    # Convert the list price to the appropriate currency if the pricelist currency is different
                                    if (
                                        pricelist_currency
                                        != line.env.company.currency_id
                                    ):
                                        converted_price = (
                                            line.product_id.list_price
                                            * line.env.company.currency_id._get_conversion_rate(
                                                line.env.company.currency_id,
                                                pricelist_currency,
                                            )
                                        )
                                    else:
                                        converted_price = line.product_id.list_price

                                    # Adjust the price_unit based on UOM and the potential currency conversion
                                    line.price_unit = converted_price * uom_ratio

                                    x = price._compute_price(
                                        line.product_id,
                                        line.product_uom_qty,
                                        line.product_uom,
                                        Datetime.now(),
                                        line.order_id.pricelist_id.currency_id,
                                    )
                                    if x != 0:
                                        if price.percent_price:
                                            line.discount = price.percent_price
                                    else:
                                        line.discount = 0

                        else:
                            if line.product_uom_qty:
                                fix = price.filtered(
                                    lambda x: x.min_quantity == line.product_uom_qty
                                )

                                if fix:
                                    if fix.fixed_price:
                                        line.price_unit = fix.fixed_price

                                    else:
                                        if line.product_id:
                                            # Get the UOM ratio to adjust the price based on the UOM
                                            uom_ratio = line.product_uom._compute_quantity(
                                                1, line.product_id.uom_id
                                            )

                                            # Get the currency of the pricelist, if it exists
                                            pricelist_currency = (
                                                line.order_id.pricelist_id.currency_id
                                                if line.order_id.pricelist_id
                                                else line.env.company.currency_id
                                            )

                                            # Convert the list price to the appropriate currency if the pricelist currency is different
                                            if (
                                                pricelist_currency
                                                != line.env.company.currency_id
                                            ):
                                                converted_price = (
                                                    line.product_id.list_price
                                                    * line.env.company.currency_id._get_conversion_rate(
                                                        line.env.company.currency_id,
                                                        pricelist_currency,
                                                    )
                                                )
                                            else:
                                                converted_price = (
                                                    line.product_id.list_price
                                                )

                                            # Adjust the price_unit based on UOM and the potential currency conversion
                                            line.price_unit = (
                                                converted_price * uom_ratio
                                            )

                                            x = fix._compute_price(
                                                line.product_id,
                                                line.product_uom_qty,
                                                line.product_uom,
                                                Datetime.now(),
                                                line.order_id.pricelist_id.currency_id,
                                            )
                                            if x != 0:
                                                if fix.percent_price:
                                                    line.discount = fix.percent_price
                                            else:
                                                line.discount = 0
                                else:
                                    max_quantity = []
                                    for x in price:
                                        if x.min_quantity < line.product_uom_qty:
                                            max_quantity.append(x.min_quantity)

                                    if max_quantity:
                                        find_max = max(max_quantity)

                                        y = price.filtered(
                                            lambda x: x.min_quantity == find_max
                                        )

                                        if y.fixed_price:
                                            if line.product_uom_qty >= y.min_quantity:
                                                line.price_unit = y.fixed_price
                                            else:
                                                if line.product_id:
                                                    # Get the UOM ratio to adjust the price based on the UOM
                                                    uom_ratio = line.product_uom._compute_quantity(
                                                        1, line.product_id.uom_id
                                                    )

                                                    # Get the currency of the pricelist, if it exists
                                                    pricelist_currency = (
                                                        line.order_id.pricelist_id.currency_id
                                                        if line.order_id.pricelist_id
                                                        else line.env.company.currency_id
                                                    )

                                                    # Convert the list price to the appropriate currency if the pricelist currency is different
                                                    if (
                                                        pricelist_currency
                                                        != line.env.company.currency_id
                                                    ):
                                                        converted_price = (
                                                            line.product_id.list_price
                                                            * line.env.company.currency_id._get_conversion_rate(
                                                                line.env.company.currency_id,
                                                                pricelist_currency,
                                                            )
                                                        )
                                                    else:
                                                        converted_price = (
                                                            line.product_id.list_price
                                                        )

                                                    # Adjust the price_unit based on UOM and the potential currency conversion
                                                    line.price_unit = (
                                                        converted_price * uom_ratio
                                                    )

                                                    # Set the discount to 0 since no pricelist item exists
                                                    line.discount = 0

                                        else:
                                            if line.product_id:
                                                # Get the UOM ratio to adjust the price based on the UOM
                                                uom_ratio = line.product_uom._compute_quantity(
                                                    1, line.product_id.uom_id
                                                )

                                                # Get the currency of the pricelist, if it exists
                                                pricelist_currency = (
                                                    line.order_id.pricelist_id.currency_id
                                                    if line.order_id.pricelist_id
                                                    else line.env.company.currency_id
                                                )

                                                # Convert the list price to the appropriate currency if the pricelist currency is different
                                                if (
                                                    pricelist_currency
                                                    != line.env.company.currency_id
                                                ):
                                                    converted_price = (
                                                        line.product_id.list_price
                                                        * line.env.company.currency_id._get_conversion_rate(
                                                            line.env.company.currency_id,
                                                            pricelist_currency,
                                                        )
                                                    )
                                                else:
                                                    converted_price = (
                                                        line.product_id.list_price
                                                    )

                                                # Adjust the price_unit based on UOM and the potential currency conversion
                                                line.price_unit = (
                                                    converted_price * uom_ratio
                                                )

                                                x = y._compute_price(
                                                    line.product_id,
                                                    line.product_uom_qty,
                                                    line.product_uom,
                                                    Datetime.now(),
                                                    line.order_id.pricelist_id.currency_id,
                                                )
                                                if x != 0:
                                                    if y.percent_price:
                                                        line.discount = y.percent_price
                                                else:
                                                    line.discount = 0

                                    else:
                                        if line.product_id:
                                            # Get the UOM ratio to adjust the price based on the UOM
                                            uom_ratio = line.product_uom._compute_quantity(
                                                1, line.product_id.uom_id
                                            )

                                            # Get the currency of the pricelist, if it exists
                                            pricelist_currency = (
                                                line.order_id.pricelist_id.currency_id
                                                if line.order_id.pricelist_id
                                                else line.env.company.currency_id
                                            )

                                            # Convert the list price to the appropriate currency if the pricelist currency is different
                                            if (
                                                pricelist_currency
                                                != line.env.company.currency_id
                                            ):
                                                converted_price = (
                                                    line.product_id.list_price
                                                    * line.env.company.currency_id._get_conversion_rate(
                                                        line.env.company.currency_id,
                                                        pricelist_currency,
                                                    )
                                                )
                                            else:
                                                converted_price = (
                                                    line.product_id.list_price
                                                )

                                            # Adjust the price_unit based on UOM and the potential currency conversion
                                            line.price_unit = (
                                                converted_price * uom_ratio
                                            )

                                            # Set the discount to 0 since no pricelist item exists
                                            line.discount = 0

                            else:
                                minimum_qu = []

                                for x in price:
                                    minimum_qu.append(x.min_quantity)

                                find_min = min(minimum_qu)

                                y = price.search([("min_quantity", "=", find_min)])

                                if y.fixed_price:
                                    if line.product_uom_qty >= y.min_quantity:
                                        line.price_unit = y.fixed_price
                                    else:
                                        if line.product_id:
                                            # Get the UOM ratio to adjust the price based on the UOM
                                            uom_ratio = line.product_uom._compute_quantity(
                                                1, line.product_id.uom_id
                                            )

                                            # Get the currency of the pricelist, if it exists
                                            pricelist_currency = (
                                                line.order_id.pricelist_id.currency_id
                                                if line.order_id.pricelist_id
                                                else line.env.company.currency_id
                                            )

                                            # Convert the list price to the appropriate currency if the pricelist currency is different
                                            if (
                                                pricelist_currency
                                                != line.env.company.currency_id
                                            ):
                                                converted_price = (
                                                    line.product_id.list_price
                                                    * line.env.company.currency_id._get_conversion_rate(
                                                        line.env.company.currency_id,
                                                        pricelist_currency,
                                                    )
                                                )
                                            else:
                                                converted_price = (
                                                    line.product_id.list_price
                                                )

                                            # Adjust the price_unit based on UOM and the potential currency conversion
                                            line.price_unit = (
                                                converted_price * uom_ratio
                                            )

                                            # Set the discount to 0 since no pricelist item exists
                                            line.discount = 0

                                else:
                                    if line.product_id:
                                        # Get the UOM ratio to adjust the price based on the UOM
                                        uom_ratio = line.product_uom._compute_quantity(
                                            1, line.product_id.uom_id
                                        )

                                        # Get the currency of the pricelist, if it exists
                                        pricelist_currency = (
                                            line.order_id.pricelist_id.currency_id
                                            if line.order_id.pricelist_id
                                            else line.env.company.currency_id
                                        )

                                        # Convert the list price to the appropriate currency if the pricelist currency is different
                                        if (
                                            pricelist_currency
                                            != line.env.company.currency_id
                                        ):
                                            converted_price = (
                                                line.product_id.list_price
                                                * line.env.company.currency_id._get_conversion_rate(
                                                    line.env.company.currency_id,
                                                    pricelist_currency,
                                                )
                                            )
                                        else:
                                            converted_price = line.product_id.list_price

                                        # Adjust the price_unit based on UOM and the potential currency conversion
                                        line.price_unit = converted_price * uom_ratio

                                        x = y._compute_price(
                                            line.product_id,
                                            line.product_uom_qty,
                                            line.product_uom,
                                            Datetime.now(),
                                            line.order_id.pricelist_id.currency_id,
                                        )
                                        if x != 0:
                                            if y.percent_price:
                                                line.discount = y.percent_price
                                        else:
                                            line.discount = 0

                    else:
                        if line.product_id:
                            # Get the UOM ratio to adjust the price based on the UOM
                            uom_ratio = line.product_uom._compute_quantity(
                                1, line.product_id.uom_id
                            )

                            # Get the currency of the pricelist, if it exists
                            pricelist_currency = (
                                line.order_id.pricelist_id.currency_id
                                if line.order_id.pricelist_id
                                else line.env.company.currency_id
                            )

                            # Convert the list price to the appropriate currency if the pricelist currency is different
                            if pricelist_currency != line.env.company.currency_id:
                                converted_price = (
                                    line.product_id.list_price
                                    * line.env.company.currency_id._get_conversion_rate(
                                        line.env.company.currency_id, pricelist_currency
                                    )
                                )
                            else:
                                converted_price = line.product_id.list_price

                            # Adjust the price_unit based on UOM and the potential currency conversion
                            line.price_unit = converted_price * uom_ratio

                            # Set the discount to 0 since no pricelist item exists
                            line.discount = 0

                else:
                    if line.product_id:
                        # Get the UOM ratio to adjust the price based on the UOM
                        uom_ratio = line.product_uom._compute_quantity(
                            1, line.product_id.uom_id
                        )

                        # Get the currency of the pricelist, if it exists
                        pricelist_currency = (
                            line.order_id.pricelist_id.currency_id
                            if line.order_id.pricelist_id
                            else line.env.company.currency_id
                        )

                        # Convert the list price to the appropriate currency if the pricelist currency is different
                        if pricelist_currency != line.env.company.currency_id:
                            converted_price = (
                                line.product_id.list_price
                                * line.env.company.currency_id._get_conversion_rate(
                                    line.env.company.currency_id, pricelist_currency
                                )
                            )
                        else:
                            converted_price = line.product_id.list_price

                        # Adjust the price_unit based on UOM and the potential currency conversion
                        line.price_unit = converted_price * uom_ratio

                        # Set the discount to 0 since no pricelist item exists
                        line.discount = 0
            else:
                line.discount = 0
                super(SaleOrderLine, line)._compute_price_unit()
