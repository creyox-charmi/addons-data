from odoo import api, fields, models, _

class EmployeeWizard(models.TransientModel):
    _name = 'cr.employee.wizard'

    name = fields.Char(string="name")
    training_record_ids = fields.One2many(comodel_name='cr.employee.training.record',
                                          inverse_name='employee_id',
                                          string='Training Records')
