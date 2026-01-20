from Cryptodome.Util.number import inverse
from odoo import api, fields, models, _

class Employee(models.Model):
    _name = 'cr.employee'

    name = fields.Char(string="name")
    mobile = fields.Char(string="Work Mobile")
    email = fields.Char(string="Work Email")
    company = fields.Char(string="Company")
    Department = fields.Char(string="Department")
    Manager = fields.Char(string="Manager")
    Coach = fields.Char(string="Coach")
    training_record_ids = fields.One2many(comodel_name='cr.employee.training.record',
                                          inverse_name='employee_id',
                                          string='Training Records')

    def action_filtered_record(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cr.employee.wizard',
            'views': [(False, 'form')],
            'target': 'new',
        }
