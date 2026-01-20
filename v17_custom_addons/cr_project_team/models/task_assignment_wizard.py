from odoo import models, fields, api

class TaskAssignmentWizard(models.TransientModel):
    _name = 'task.assignment.wizard'
    _description = 'Task Assignment Wizard'

    project_id = fields.Many2one(comodel_name='project.team',
                                 string='Project',
                                 required=True)
    team_member_ids = fields.Many2many(comodel_name='project.team.member',
                                       string='Team Members',
                                       required=True)

    def action_assign_tasks(self):
        self.ensure_one()
        tasks = self.env['project.task'].search([('project_id', '=', self.project_id.id)])
        for task in tasks:
            task.write({'assigned_to_ids': [(4, partner.id) for partner in self.team_member_ids]})
        return {'type': 'ir.actions.act_window_close'}
