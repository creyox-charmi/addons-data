from odoo import models, fields

class ProjectTeamMember(models.Model):
    _name = 'project.team.member'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    role = fields.Char(string='Role')
    project_ids = fields.Many2many(comodel_name='project.team',
                                   string='Projects')
