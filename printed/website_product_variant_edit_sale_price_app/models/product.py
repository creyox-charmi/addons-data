# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from itertools import chain
from odoo.http import request

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    set_attribute_price = fields.Boolean(string='Set Attribute Price', default=False)

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        """Override for website, where we want to:
            - take the website pricelist if no pricelist is set
            - apply the b2b/b2c setting to the result

        This will work when adding website_id to the context, which is done
        automatically when called from routes with website=True.
        """
        print("CALLLLLLLLLLLLLLLLLLLLLLL")
        self.ensure_one()

        current_website = False

        product_template = self

        combination = combination or product_template.env['product.template.attribute.value']

        if not product_id and not combination and not only_template:
            combination = product_template._get_first_possible_combination(parent_combination)

        if only_template:
            product = product_template.env['product.product']
        elif product_id and not combination:
            product = product_template.env['product.product'].browse(product_id)
        else:
            product = product_template._get_variant_for_combination(combination)

        if self.env.context.get('website_id'):
            current_website = self.env['website'].get_current_website()
            print(">>",current_website.pricelist_id)
            if not pricelist:
                print("yesss")
                pricelist = current_website.pricelist_id

        print("combination : ",combination)
        print("product_id : ", product_id)
        print("add_qty : ", add_qty)
        print("pricelist : ", pricelist)
        print("parent_combination : ", parent_combination)

        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty,parent_combination=parent_combination, only_template=only_template)

        print("1 > ",combination_info)

        if self.env.context.get('website_id'):
            context = dict(self.env.context, ** {
                'quantity': self.env.context.get('quantity', add_qty),
                'pricelist': pricelist and pricelist.id
            })

            product = (self.env['product.product'].browse(combination_info['product_id']) or self).with_context(context)
            partner = self.env.user.partner_id
            company_id = current_website.company_id

            tax_display = self.env.user.has_groups('account.group_show_line_subtotals_tax_excluded') and 'total_excluded' or 'total_included'
            fpos = self.env['account.fiscal.position'].sudo()._get_fiscal_position(partner)
            product_taxes = product.sudo().taxes_id.filtered(lambda x: x.company_id == company_id)
            taxes = fpos.map_tax(product_taxes)

            # The list_price is always the price of one.
            quantity_1 = 1
            combination_info['price'] = self.env['account.tax']._fix_tax_included_price_company(
                combination_info['price'], product_taxes, taxes, company_id)
    
            price = taxes.compute_all(combination_info['price'], pricelist.currency_id, quantity_1, product, partner)[tax_display]
            print('price : ',price)
            print("zzz")
            # if pricelist.discount_policy == 'without_discount':
            #     combination_info['list_price'] = self.env['account.tax']._fix_tax_included_price_company(
            #         combination_info['list_price'], product_taxes, taxes, company_id)
            #     list_price = taxes.compute_all(combination_info['list_price'], pricelist.currency_id, quantity_1, product, partner)[tax_display]
            # else:
            #     list_price = price



            list_price = price
            print('list_price : ', list_price)
            if product:
                print(">>y")
                if pricelist:
                    print(">>1")
                    price = pricelist.with_context(new_list_price=True)._get_product_price(product, quantity_1)
                    print('price : ',price)
                else:
                    print(">>2")
                    price = list_price
                    print('price : ',price)
                list_price = product.price_compute('list_price')[product.id]
                print('list_price : ',list_price)
            else:
                print(">>N")
                list_price = product_template.price_compute('list_price')[product_template.id]
                if pricelist:
                    price = pricelist._get_product_price(product_template, quantity_1)
                else:
                    price = list_price
        
            has_discounted_price = pricelist.currency_id.compare_amounts(list_price, price) == 1
            # if self.set_attribute_price:
            #     if combination_info.get('product_id'):
            #         if pricelist.discount_policy == 'without_discount':
            #             if product.new_list_price > price:
            #                 has_discounted_price = True
            #             else:
            #                 has_discounted_price = False
            #         else:
            #             has_discounted_price = False

            if self.set_attribute_price:
                if combination_info.get('product_id'):
                    if product.new_list_price > price:
                        print("ha")
                        has_discounted_price = True
                    else:
                        print("na")
                        has_discounted_price = False

            combination_info.update(
                base_unit_name=product.base_unit_name,
                base_unit_price=product.base_unit_price,
                price=price,
                list_price=list_price,
                has_discounted_price=has_discounted_price
            )
            print('combination_info :  ',combination_info)

        return combination_info

class ProductProduct(models.Model):
    _inherit = "product.product"

    is_true = fields.Boolean(string='is_true', default=True)
    new_list_price = fields.Float(
        'Sales Price', store=True,
        digits='Product Price',
        help="The sale price is managed from the product template. Click on the 'Configure Variants' button to set the extra attribute prices.")

    
    @api.depends('list_price', 'new_list_price', 'price_extra')
    @api.depends_context('uom')
    def _compute_product_lst_price(self):
        print("PRODUCT")
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse(self._context['uom'])

        for product in self:
            if product.set_attribute_price == True:
                if to_uom:
                    new_list_price = product.uom_id._compute_price(product.new_list_price, to_uom)
                else:
                    new_list_price = product.new_list_price
                product.lst_price = new_list_price + product.price_extra
                product.update({'lst_price' : new_list_price + product.price_extra})
            else:
                if to_uom:
                    list_price = product.uom_id._compute_price(product.list_price, to_uom)
                else:
                    list_price = product.list_price
                product.lst_price = list_price + product.price_extra

    def price_compute(self, price_type, uom=None, currency=None, company=None, date=False,):
        print(">>>>>>>>>>>price_compute>>>>>>>>>>>>")
        print('price_type : ',price_type)
        company = company or self.env.company
        date = date or fields.Date.context_today(self)

        self = self.with_company(company)
        print('self : ', self)
        if price_type == 'standard_price':
            print('1>>if price_type ==  ')
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            self = self.sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        print('prices : ', prices)
        for product in self:
            print("------------------------------------")
            print('product : ', product)
            price = product[price_type] or 0.0
            print('price : ', price)
            price_currency = product.currency_id
            print('price_currency : ', price_currency)
            if price_type == 'standard_price':
                print("if price_type == 'standard_price':>>true")
                print('price_type : ', price_type)
                price_currency = product.cost_currency_id
                print('price_currency : ', price_currency)

            if price_type == 'list_price':
                print("if price_type == 'list_price': >> true")
                price += product.price_extra
                # we need to add the price from the attributes that do not generate variants
                # (see field product.attribute create_variant)
                if self._context.get('no_variant_attributes_price_extra'):
                    # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    price += sum(self._context.get('no_variant_attributes_price_extra'))

            if product.set_attribute_price == True:
                print("if product.set_attribute_price == True:>>true")
                if price_type == 'new_list_price':
                    prices[product.id] += product.price_extra
                    # we need to add the price from the attributes that do not generate variants
                    # (see field product.attribute create_variant)
                    if self._context.get('no_variant_attributes_price_extra'):
                        # we have a list of price_extra that comes from the attribute values, we need to sum all that
                        prices[product.id] += sum(self._context.get('no_variant_attributes_price_extra'))
                if product.new_list_price:
                    print("if product.new_list_price: >> true")
                    price = product.new_list_price
                    print("price : ",price)
                else:
                    print("else")
                    price = price
                    print("price : ", price)

            if uom:
                print("if uom:>>true")
                price = product.uom_id._compute_price(price, uom)
                print("price : ", price)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                print("if currency:>>true")
                price = price_currency._convert(price, currency, company, date)
                print("price : ", price)
                
            prices[product.id] = price
            print("prices[product.id] : ", prices[product.id])
            print("price : ", price)
        return prices

    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        res = super()._price_compute(price_type, uom=None, currency=None, company=None, date=False)
        print("res>>>>>>>>",res)
        prices = dict.fromkeys(self.ids, 0.0)
        for product in self:
            if price_type == 'list_price':
                price_currency = product.currency_id
                if product.is_true:
                    if product.new_list_price:
                        print('|||||||product._get_attributes_extra_price() : ',product._get_attributes_extra_price())
                        price = product.new_list_price + product._get_attributes_extra_price()

                        if uom:
                            print("if uom: >> true")
                            price = product.uom_id._compute_price(price, uom)
                            print("price : ", price)

                            # Convert from current user company currency to asked one
                            # This is right cause a field cannot be in more than one currency
                        if currency:
                            print("if currency: >> true")
                            price = price_currency._convert(price, currency, company, date)
                            print("price : ", price)

                        prices[product.id] = price
                        res[product.id] = price
                print("prices[product.id] : ", prices[product.id])

        return res



class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule(self, products, quantity, uom=None, date=False,compute_price=True, **kwargs):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        :param products: recordset of products (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
            If not specified, prices returned are expressed in product uoms
        :param date: date to use for price computation and currency conversions
        :type date: date or datetime

        :returns: product_id: (price, pricelist_rule)
        :rtype: dict
        """
        self.ensure_one()



        if not products:
            print("if not products >> true")
            return {}

        if not date:
            print("if not date >> true")
            # Used to fetch pricelist rules and currency rates
            date = fields.Datetime.now()

        # Fetch all rules potentially matching specified products/templates/categories and date
        rules = self._get_applicable_rules(products, date, **kwargs)
        print("rules : ",rules)

        results = {}
        for product in products:
            print("----------------------------------------------------------")
            print("product : ",product)
            suitable_rule = self.env['product.pricelist.item']
            print("suitable_rule : ", suitable_rule)

            product_uom = product.uom_id
            print("product_uom : ", product_uom)
            target_uom = uom or product_uom  # If no uom is specified, fall back on the product uom
            print("target_uom : ", target_uom)

            # Compute quantity in product uom because pricelist rules are specified
            # w.r.t product default UoM (min_quantity, price_surchage, ...)
            if target_uom != product_uom:
                print("if target_uom != product_uom: >> true")
                qty_in_product_uom = target_uom._compute_quantity(quantity, product_uom, raise_if_failure=False)
                print("qty_in_product_uom : ", qty_in_product_uom)
            else:
                print("elseee")
                qty_in_product_uom = quantity
                print("qty_in_product_uom : ", qty_in_product_uom)

            for rule in rules:
                print("----------------------------------------------------------")
                if rule._is_applicable_for(product, qty_in_product_uom):
                    print("if rule._is_applicable_for(product, qty_in_product_uom) >>true")
                    suitable_rule = rule
                    print("suitable_rule : ",suitable_rule)
                    break
            
            if product._name == 'product.product':
                print("if product._name == 'product.product': >> true")
                if self._context.get('new_list_price') == True:
                    print("if self._context.get('new_list_price') == True: >> true")
                    price = product.price_compute('new_list_price')[product.id]
                    print("price : ",price)
                else:
                    print("elsee")
                    price = product.price_compute('list_price')[product.id]
                    print("price : ", price)


            kwargs['pricelist'] = self
            print("kwargs['pricelist'] : ",kwargs['pricelist'])
            price = suitable_rule._compute_price(product, quantity, target_uom, date=date, currency=self.currency_id)
            print("price : ", price)
            print("{{{{{{{{{{{{{{{")
            results[product.id] = (price, suitable_rule.id)
            print("{{{{{{{{{{{{{{{")
            print("results[product.id] : ", results[product.id])
            print("results : ", results)
            print("{{{{{{{{{{{{{{{")

        return results

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

