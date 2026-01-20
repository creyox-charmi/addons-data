from odoo import api, fields, models, _

class ProductReview(models.Model):
    _name = 'product.review'

    product_id = fields.Many2one(string="product_id",
                                 comodel_name='product',
                                 required=True)
    product_price = fields.Integer(string='price',
                                related='product_id.price',
                                store=True)
    customer_name = fields.Char(string="customer_name")
    rating =  fields.Selection([('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'), ('very good', 'Very Good'), ('excellent', 'Excellent')], string='Rating', required=True)
    comment = fields.Text(string='comment')
    review_date = fields.Date(string='review_date')


