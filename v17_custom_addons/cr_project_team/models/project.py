from odoo import api, fields, models, _

class Project(models.Model):
    _name = 'project.team'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    team_member_ids = fields.Many2many(string="team_member_ids",
                                       comodel_name="project.team.member")
    task_ids = fields.One2many(comodel_name='project.task',
                               inverse_name='project_id',
                               string='task_ids')

    def action_get_team_member_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Team Member',
            'view_mode': 'tree,form',
            'domain':[('project_ids','=',self.id)],
            'res_model': 'project.team.member',
        }

    def action_get_task_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'view_mode': 'tree,form',
            'domain':[('project_id','=',self.id)],
            'res_model': 'project.task',
        }

    def action_task_assign_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'task.assignment.wizard',
            'views': [(False, 'form')],
            'target': 'new',
        }