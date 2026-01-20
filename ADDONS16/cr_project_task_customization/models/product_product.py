from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    cr_odoo_service = fields.Boolean(string="Is Odoo Service?", default=False)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cr_odoo_service = fields.Boolean(string="Is Odoo Service?", default=False)
