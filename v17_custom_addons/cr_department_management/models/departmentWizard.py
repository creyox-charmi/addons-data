from odoo import models, fields, api

class DepartmentWizard(models.TransientModel):
    _name = 'cr.department.wizard'
    _description = 'Department Wizard'

    type = fields.Selection([('create', 'Create'), ('write', 'Write')], string='Type', required=True)
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    department_id = fields.Many2one(comodel_name='cr.department.department',
                                    string='Department')

    def action_process(self):
        if self.type == 'create':
            self.env['cr.department.department'].create({
                'name': self.name,
                'code': self.code,
            })
        elif self.type == 'write':
            if self.department_id:
                self.department_id.write({
                    'name': self.name,
                    'code': self.code,
                })
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
