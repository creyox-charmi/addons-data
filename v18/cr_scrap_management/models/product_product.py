from odoo import api, Command, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError


class Product(models.Model):
    _inherit = 'product.product'