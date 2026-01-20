# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quantity_set = fields.Integer(string='Bulk Quantity', default=1)
    multi_quantity_product = fields.Integer(
        string="Multiple Quantity ",
        default=1,
        store=True,
        help="Quantity increase/decrease in multiples of this value"
    )
    website_quantity_ids = fields.One2many('multi.website.quantity', 'product_id', string='Quantity')
    multi_quantity_check = fields.Boolean(compute='compute_multi_quantity_check')

    def compute_multi_quantity_check(self):
        """
        Compute method to check if the multi-quantity feature is enabled 
        for the company associated with the current user.
        """
        for data in self:
            data.multi_quantity_check = data.env.user.company_id.multi_quantity_on_multi_product

    @api.depends('multi_quantity_check', 'quantity_set')
    def set_multi_quantity_product(self, current_website_id):
        """
        Compute method to set the `multi_quantity_product` field based on the current website.
        If `multi_quantity_check` is enabled, it retrieves the quantity defined for the current website.
        Otherwise, it falls back to the default `quantity_set` value.

        :param current_website_id: ID of the current website.
        """
        for rec in self:
            if rec.multi_quantity_check:
                quantity = rec.website_quantity_ids.filtered(
                    lambda record: record.website_id.id == current_website_id
                ).mapped('quantity')
                print('Quantity:', quantity)
                rec.multi_quantity_product = quantity[0] if quantity else 1
            else:
                rec.multi_quantity_product = rec.quantity_set


