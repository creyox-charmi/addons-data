# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _
import datetime


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")

    @api.onchange("invoice_line_ids", "product_uom_id", "pricelist_id")
    def onchange_product(self):
        for line in self.invoice_line_ids:
            if self.pricelist_id and self.partner_id and line.product_id:
                if line.product_id.product_tmpl_id.attribute_line_ids:
                    each_price = self.pricelist_id.item_ids.search(
                        [
                            ("product_id", "=", line.product_id.id),
                            ("pricelist_id", "=", self.pricelist_id.id),
                            ("uom_id", "=", line.product_uom_id.id),
                        ]
                    )
                else:
                    each_price = self.pricelist_id.item_ids.search(
                        [
                            (
                                "product_tmpl_id",
                                "=",
                                line.product_id.product_tmpl_id.id,
                            ),
                            ("pricelist_id", "=", self.pricelist_id.id),
                            ("uom_id", "=", line.product_uom_id.id),
                        ]
                    )
                if each_price:
                    if len(each_price) == 1:
                        if each_price.fixed_price:
                            if line.quantity >= each_price.min_quantity:
                                line.price_unit = each_price.fixed_price
                                line.discount = 0
                            else:
                                if line.product_id:
                                    # Get the UOM ratio to adjust the price based on the UOM
                                    uom_ratio = line.product_uom_id._compute_quantity(
                                        1, line.product_id.uom_id
                                    )

                                    # Get the currency of the pricelist, if it exists
                                    pricelist_currency = (
                                        self.pricelist_id.currency_id
                                        if self.pricelist_id
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
                                uom_ratio = line.product_uom_id._compute_quantity(
                                    1, line.product_id.uom_id
                                )

                                # Get the currency of the pricelist, if it exists
                                pricelist_currency = (
                                    self.pricelist_id.currency_id
                                    if self.pricelist_id
                                    else line.env.company.currency_id
                                )

                                # Convert the list price to the appropriate currency if the pricelist currency is different
                                if pricelist_currency != line.env.company.currency_id:
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

                                x = each_price._compute_price(
                                    line.product_id,
                                    line.quantity,
                                    line.product_uom_id,
                                    datetime.datetime.now(),
                                    self.pricelist_id.currency_id,
                                )
                                if x != 0:
                                    if each_price.percent_price:
                                        line.discount = each_price.percent_price
                                else:
                                    line.discount = 0
                    else:
                        if line.quantity:
                            fix = each_price.filtered(
                                lambda x: x.min_quantity == line.quantity
                            )
                            # fix = price.search([('min_quantity','=',line.product_uom_qty),('uom_id','=',line.product_uom.id)])

                            if fix:
                                if fix.fixed_price:
                                    line.price_unit = fix.fixed_price
                                    line.discount = 0

                                else:
                                    if line.product_id:
                                        # Get the UOM ratio to adjust the price based on the UOM
                                        uom_ratio = line.product_uom_id._compute_quantity(
                                            1, line.product_id.uom_id
                                        )

                                        # Get the currency of the pricelist, if it exists
                                        pricelist_currency = (
                                            self.pricelist_id.currency_id
                                            if self.pricelist_id
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

                                        x = fix._compute_price(
                                            line.product_id,
                                            line.quantity,
                                            line.product_uom_id,
                                            datetime.datetime.now(),
                                            self.pricelist_id.currency_id,
                                        )
                                        if x != 0:
                                            if fix.percent_price:
                                                line.discount = fix.percent_price
                                        else:
                                            line.discount = 0
                            else:
                                max_quantity = []
                                for x in each_price:

                                    if x.min_quantity < line.quantity:
                                        max_quantity.append(x.min_quantity)

                                if max_quantity:
                                    find_max = max(max_quantity)

                                    y = each_price.filtered(
                                        lambda x: x.min_quantity == find_max
                                    )

                                    if y.fixed_price:
                                        if line.quantity >= y.min_quantity:
                                            line.price_unit = y.fixed_price
                                            line.discount = 0
                                        else:
                                            if line.product_id:
                                                # Get the UOM ratio to adjust the price based on the UOM
                                                uom_ratio = line.product_uom_id._compute_quantity(
                                                    1, line.product_id.uom_id
                                                )

                                                # Get the currency of the pricelist, if it exists
                                                pricelist_currency = (
                                                    self.pricelist_id.currency_id
                                                    if self.pricelist_id
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
                                            uom_ratio = line.product_uom_id._compute_quantity(
                                                1, line.product_id.uom_id
                                            )

                                            # Get the currency of the pricelist, if it exists
                                            pricelist_currency = (
                                                self.pricelist_id.currency_id
                                                if self.pricelist_id
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
                                                line.quantity,
                                                line.product_uom_id,
                                                datetime.datetime.now(),
                                                self.pricelist_id.currency_id,
                                            )
                                            if x != 0:
                                                if y.percent_price:
                                                    line.discount = y.percent_price
                                            else:
                                                line.discount = 0

                                else:
                                    if line.product_id:
                                        # Get the UOM ratio to adjust the price based on the UOM
                                        uom_ratio = line.product_uom_id._compute_quantity(
                                            1, line.product_id.uom_id
                                        )

                                        # Get the currency of the pricelist, if it exists
                                        pricelist_currency = (
                                            self.pricelist_id.currency_id
                                            if self.pricelist_id
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
                            minimum_qu = []

                            for x in each_price:
                                minimum_qu.append(x.min_quantity)

                            find_min = min(minimum_qu)

                            y = each_price.search([("min_quantity", "=", find_min)])

                            if y.fixed_price:
                                if line.product_uom_qty >= y.min_quantity:
                                    line.price_unit = y.fixed_price
                                else:
                                    if line.product_id:
                                        # Get the UOM ratio to adjust the price based on the UOM
                                        uom_ratio = line.product_uom_id._compute_quantity(
                                            1, line.product_id.uom_id
                                        )

                                        # Get the currency of the pricelist, if it exists
                                        pricelist_currency = (
                                            self.pricelist_id.currency_id
                                            if self.pricelist_id
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
                                    uom_ratio = line.product_uom_id._compute_quantity(
                                        1, line.product_id.uom_id
                                    )

                                    # Get the currency of the pricelist, if it exists
                                    pricelist_currency = (
                                        self.pricelist_id.currency_id
                                        if self.pricelist_id
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

                                    x = each_price._compute_price(
                                        line.product_id,
                                        line.quantity,
                                        line.product_uom_id,
                                        datetime.datetime.now(),
                                        self.pricelist_id.currency_id,
                                    )
                                    if x != 0:
                                        if each_price.percent_price:
                                            line.discount = each_price.percent_price
                                    else:
                                        line.discount = 0

                else:
                    if line.product_id:
                        if line.product_id:
                            # Get the UOM ratio to adjust the price based on the UOM
                            uom_ratio = line.product_uom_id._compute_quantity(
                                1, line.product_id.uom_id
                            )

                            # Get the currency of the pricelist, if it exists
                            pricelist_currency = (
                                self.pricelist_id.currency_id
                                if self.pricelist_id
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
                    if line.product_id:
                        # Get the UOM ratio to adjust the price based on the UOM
                        uom_ratio = line.product_uom_id._compute_quantity(
                            1, line.product_id.uom_id
                        )

                        # Get the currency of the pricelist, if it exists
                        pricelist_currency = (
                            self.pricelist_id.currency_id
                            if self.pricelist_id
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

    @api.model
    def create(self, val):
        res = super(AccountMoveInherit, self).create(val)
        if self._context.get("active_model") == "sale.order":
            sale_obj = self.env["sale.order"].browse(self._context.get("active_id"))
            res.pricelist_id = sale_obj.pricelist_id
        return res
