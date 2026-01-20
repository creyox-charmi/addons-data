from fields.extras import ValidationError
from odoo import api, fields, models, _

class Product(models.Model):
    """_name is display in the url when we are open department(table) of models(database) """
    _name = 'cr.inventory.product'
    _description = 'Product'

    name = fields.Char(string='Product Name', required=True)
    category_id = fields.Many2one('cr.inventory.category', string='Category')
    supplier_id = fields.Many2one('cr.inventory.supplier', string='Supplier')
    supplier_name = fields.Char(string="Supplier_name", related="supplier_id.name", store=True)
    price = fields.Float(string='Price')
    quantity = fields.Integer(string='Quantity')
    total_value = fields.Float(string='Total Value', compute='_compute_total_value', store=True)

    @api.depends('price', 'quantity')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.price * record.quantity

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity < 0:
            raise ValidationError("Quantity must be greater than zero!")

    def action_filtered_record(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cr.product.wizard',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def action_get_supplier_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Supplier',
            'view_mode': 'tree,form',
            'domain':[('id','=',self.supplier_id.id)],
            'res_model': 'cr.inventory.supplier',
        }

    def action_getObject_record(self):
        print(self)