# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _
import datetime


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "product_uom", "product_id", "order_id.pricelist_id", "product_uom_qty"
    )
    def _compute_price_unit(self):
        for line in self:
            super(SaleOrderLine, line)._compute_price_unit()
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
                                    x = self.check_date(line, price)
                                    if x == True:
                                        line.price_unit = price.fixed_price
                                        line.discount = 0
                                    else:
                                        self.a(line)
                                else:
                                    self.a(line)

                            else:
                                x = self.b(line, price)
                                if x != 0:
                                    if price.percent_price:
                                        y = self.check_date(line, price)
                                        if y == True:
                                            line.discount = price.percent_price
                                        else:
                                            self.a(line)
                                else:
                                    self.a(line)

                        else:
                            if line.product_uom_qty:
                                fix = price.filtered(
                                    lambda x: x.min_quantity == line.product_uom_qty
                                )

                                if fix:
                                    if fix.fixed_price:
                                        x = self.check_date(line, fix)
                                        if x == True:
                                            line.price_unit = fix.fixed_price
                                            line.discount = 0
                                        else:
                                            self.multiple_pricelist(price, line)


                                    else:
                                        x = self.b(line, fix)

                                        if x != 0:
                                            if fix.percent_price:
                                                y = self.check_date(line, fix)
                                                if y == True:
                                                    line.discount = fix.percent_price

                                                else:
                                                    self.multiple_pricelist(price, line)
                                        else:
                                            self.a(line)
                                else:
                                    self.multiple_pricelist(price, line)
                            else:
                                self.a(line)
                    else:
                        self.a(line)
                else:
                    self.a(line)
            else:
                line.discount = 0

    def a(self, line):
        if line.product_id:
            # Get the UOM ratio to adjust the price based on the UOM
            uom_ratio = line.product_uom._compute_quantity(
                1, line.product_id.uom_id
            )

            # Get the currency of the pricelist, if it exists
            pricelist_currency = (
                self.order_id.pricelist_id.currency_id
                if self.order_id.pricelist_id
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

            line.discount = 0

    def check_date(self, line, price):
        flag = False
        if price.date_start and not price.date_end:
            if price.date_start <= datetime.datetime.now():
                flag = True

        elif not price.date_start and price.date_end:
            if price.date_end >= datetime.datetime.now():
                flag = True

        elif price.date_start and price.date_end:
            if price.date_start <= datetime.datetime.now() and price.date_end >= datetime.datetime.now():
                flag = True

        else:
            flag = True

        return flag

    def b(self, line, price):
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
                datetime.datetime.now(),
                line.order_id.pricelist_id.currency_id,
            )
        return x

    def multiple_pricelist(self, price, line):
        max_quantity = []
        for x in price:
            if x.min_quantity < line.product_uom_qty:
                max_quantity.append(x.min_quantity)

        if max_quantity:
            elements = sorted(max_quantity)
            elements.reverse()
            flag = 0
            for element in elements:
                filter_record = price.filtered(
                    lambda x: x.min_quantity == element
                )

                if filter_record.fixed_price:
                    if line.product_uom_qty >= filter_record.min_quantity:
                        x = self.check_date(line, filter_record)
                        if x == True:
                            flag = 1
                            line.price_unit = filter_record.fixed_price
                            line.discount = 0
                            break

                else:
                    x = self.b(line, filter_record)
                    if x != 0:
                        if filter_record.percent_price:
                            y = self.check_date(line, filter_record)
                            if y == True:
                                flag = 1
                                line.discount = filter_record.percent_price
                                break

                if flag == 0:
                    self.a(line)
        else:
            self.a(line)
