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
                                x = self.check_date(line, each_price)
                                if x == True:
                                    line.price_unit = each_price.fixed_price
                                    line.discount = 0
                                else:
                                    self.a(line)

                            else:
                                self.a(line)

                        else:
                            x = self.b(line, each_price)
                            if x != 0:
                                if each_price.percent_price:
                                    y = self.check_date(line, each_price)
                                    if y == True:
                                        line.discount = each_price.percent_price
                                    else:
                                        self.a(line)
                            else:
                                self.a(line)
                    else:
                        if line.quantity:
                            fix = each_price.filtered(
                                lambda x: x.min_quantity == line.quantity
                            )

                            if fix:
                                if fix.fixed_price:
                                    x = self.check_date(line, fix)
                                    if x == True:
                                        line.price_unit = fix.fixed_price
                                        line.discount = 0
                                    else:
                                        self.multiple_pricelist(each_price, line)


                                else:
                                    x = self.b(line, fix)
                                    if x != 0:
                                        if fix.percent_price:
                                            y = self.check_date(line, fix)
                                            if y == True:
                                                line.discount = fix.percent_price
                                            else:
                                                self.multiple_pricelist(fix, line)
                                    else:
                                        self.a(line)
                            else:
                                self.multiple_pricelist(each_price, line)
                        else:
                            self.a(line)
                else:
                    self.a(line)
            else:
                self.a(line)

    def a(self, line):
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

    @api.model
    def create(self, val):
        res = super(AccountMoveInherit, self).create(val)
        if self._context.get("active_model") == "sale.order":
            sale_obj = self.env["sale.order"].browse(self._context.get("active_id"))
            res.pricelist_id = sale_obj.pricelist_id
        return res

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

    def b(self, line, each_price):
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
        return x

    def multiple_pricelist(self, price, line):
        max_quantity = []
        for x in price:
            if x.min_quantity < line.quantity:
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
                    if line.quantity >= filter_record.min_quantity:
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
