from odoo import api, fields, models, _

class EmployeeTrainingRecord(models.Model):
    _name = 'cr.employee.training.record'

    employee_id = fields.Many2one(comodel_name="cr.employee" , string="Employee")
    training_id = fields.Many2one(comodel_name="cr.training.session" ,
                                  string="Training Session")
    status = fields.Selection([
        ('Completed','Completed'),
        ('In Progress','In Progress'),
        ('Not Started','Not Started')
    ],string='Status',default='Not Started')
    feedback = fields.Text(string="Feedback")
    employee_name = fields.Char(related='employee_id.name', string='Employee Name', readonly=True)
    employee_company = fields.Char(related='employee_id.company', string='Job Title', readonly=True)
    training_name = fields.Char(related='training_id.name', string='Training Name', readonly=True)
    training_date = fields.Date(related='training_id.date', string='Training Date', readonly=True)
    training_trainer = fields.Char(related='training_id.trainer', string='Trainer', readonly=True)

