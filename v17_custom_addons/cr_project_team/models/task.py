from odoo import api, fields, models, _

class Task(models.Model):
    _name = 'project.task'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    due_date = fields.Date(string="Due Date")
    project_id = fields.Many2one(comodel_name='project.team',
                                 string='project_id')
    assigned_to_ids = fields.Many2many(comodel_name='project.team.member',
                                       string='Assigned To')
    project_name = fields.Char(related='project_id.name', string='Project Name', store=True)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.assigned_to_ids = self.project_id.team_member_ids