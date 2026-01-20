from odoo import api, fields, models, _

class Product(models.TransientModel):
    _name = 'product.wizard'

    name = fields.Char(string="name")
    price = fields.Integer(string="price")
    review_id = fields.One2many(string="review_id",
                                comodel_name='product.review',
                                inverse_name='product_id')




