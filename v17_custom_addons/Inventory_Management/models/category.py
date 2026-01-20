from odoo import api, fields, models, _

class Product(models.Model):
    """_name is display in the url when we are open department(table) of models(database) """
    _name = 'cr.inventory.category'
    _description = 'Category'

    name = fields.Char(string='Category Name', required=True)
    product_ids = fields.One2many('cr.inventory.product', 'category_id', string='Products')
    info = fields.Text(string='Info')
