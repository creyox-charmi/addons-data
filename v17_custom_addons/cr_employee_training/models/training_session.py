from odoo import api, fields, models, _

class TrainingSession(models.Model):
    _name = 'cr.training.session'

    name = fields.Char(string="name")
    date = fields.Date(string="Session Date")
    trainer = fields.Char(string="Trainer's Name")
    description = fields.Text(string="Description")
    no_of_trainner = fields.Integer(string="no_of_trainner", compute="_compute_no_of_trainner", store=True)
    employee_training_ids = fields.One2many(comodel_name='cr.employee.training.record',
                                            inverse_name='training_id',
                                            string='Employee Trainings')

    @api.depends('employee_training_ids')
    def _compute_no_of_trainner(self):
        for dep in self:
            dep.no_of_trainner = len(dep.employee_training_ids)

    def action_get_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'student',
            'view_mode': 'tree,form',
            'res_model': 'cr.employee.training.record',
            'domain': [('training_id', '=', self.id)],
            'context': "{'create': False}"
        }
