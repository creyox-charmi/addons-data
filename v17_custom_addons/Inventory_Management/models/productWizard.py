from fields.extras import ValidationError
from odoo import models, fields, api

class DepartmentWizard(models.TransientModel):
    _name = 'cr.product.wizard'
    _description = 'Stock Update'

    type = fields.Selection([('create', 'Create'), ('write', 'Write')], string='Type', required=True)
    name = fields.Char(string='Name')
    category_id = fields.Many2one(comodel_name='cr.inventory.category',
                                    string='Category')
    supplier_id = fields.Many2one(comodel_name='cr.inventory.supplier',
                                  string='Supplier')
    price = fields.Float(string='Price')
    quantity = fields.Integer(string='Quantity')
    total_value = fields.Float(string='Total Value', compute='_compute_total_value', store=True)


    def action_process(self):
        if self.type == 'create':
            self.env['cr.inventory.product'].create({
                'name': self.name,
                'price': self.price,
                'quantity':self.quantity,
                'total_value':self.total_value
            })
        elif self.type == 'write':
            if self.product_id:
                self.product_id.write({
                    'name': self.name,
                    'price': self.price,
                    'quantity':self.quantity,
                    'total_value':self.total_value
                })
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.depends('price', 'quantity')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.price * record.quantity

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity < 0:
            raise ValidationError("Quantity must be greater than zero!")