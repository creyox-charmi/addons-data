# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class NotificationConfig(models.Model):
    _name = 'notification.config'
    _description = 'Notification Config'

    @api.onchange('model_id', 'on_state_change')
    def onchange_selection_fields(self):
        """This method raise validation error if selected model has no any selection field and user wants notification
            on state change
        """
        for record in self:
            if record.model_id and record.on_state_change:
                state_fields = self.env['ir.model.fields'].search(
                    [('model_id', '=', record.model_id.id), ('ttype', '=', 'selection')]).mapped('id')
                if not state_fields:
                    raise ValidationError('Selected model has no any state field.')

    name = fields.Char()
    notify_user_ids = fields.Many2many('res.users')
    model_id = fields.Many2one('ir.model')
    field_id = fields.Many2one('ir.model.fields')
    on_create = fields.Boolean()
    on_state_change = fields.Boolean()
    is_sticky = fields.Boolean()
    state_ids = fields.Many2many('state.value')
    on_create_action_id = fields.Many2one('base.automation', copy=False)
    on_change_action_id = fields.Many2one('base.automation', copy=False)
    notification_type = fields.Selection(
        [('default', 'Default'), ('info', 'Info'), ('warning', 'Warning'), ('success', 'Success'),
         ('danger', 'Danger')], default='info')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft')

    def reset_to_draft(self):
        """This method update the status of User Notify Configuration to Draft"""
        self.ensure_one()
        self.state = 'draft'
        if self.on_create_action_id:
            self.on_create_action_id.active = False
        if self.on_change_action_id:
            self.on_change_action_id.active = False

    def unlink(self):
        """This method archived linked automated actions with this notification record"""
        for notify in self:
            if notify.on_create_action_id:
                notify.on_create_action_id.unlink()
            if notify.on_change_action_id:
                notify.on_change_action_id.unlink()
        return super().unlink()

    def action_confirm(self):
        """This method updates the status of User Notify Configuration to Confirm
            Also, check if action is already created then it will update it otherwise create"""
        self.ensure_one()
        self.state = 'confirmed'
        base_automation = self.env['base.automation']
        if self.on_create:
            if not self.on_create_action_id:
                on_create_action_id = base_automation.create({
                    'name': 'User notification on create of %s ' % self.model_id.name,
                    'is_notify_action': True,
                    'model_id': self.model_id.id,
                    'trigger': 'on_create',
                })
                code_line = []
                code_line.append((0,0,{
                                    'name': 'User notification on create of %s ' % self.model_id.name,
                                    'model_id': self.model_id.id,
                                    'state': 'code',
                                    'code': f"""for rec in records:\n  env.user.sudo().generate_notification_on_record_create(notification_config_id={self.id}, record=rec)""",
                                  }))
                on_create_action_id.action_server_ids = code_line
                if on_create_action_id:
                    self.on_create_action_id = on_create_action_id.id
            else:
                self.on_create_action_id.write({
                    'active': True,
                    'is_notify_action': True,
                    'name': 'User notification on create of %s ' % self.model_id.name,
                    'trigger': 'on_create',
                })
                self.on_create_action_id.action_server_ids.model_id =  self.model_id.id
                self.on_create_action_id.action_server_ids.state =  'code'
                self.on_create_action_id.action_server_ids.code =  f"""for rec in records:\n  env.user.sudo().generate_notification_on_record_create(notification_config_id={self.id}, record=rec)"""
        else:
            if self.on_create_action_id:
                self.on_create_action_id.write({'active': False})

        if self.on_state_change:
            if not self.on_change_action_id:
                on_change_action_id = base_automation.create({
                    'name': f'User notification on {self.field_id.field_description} change of {self.model_id.name}',
                    'is_notify_action': True,
                    'model_id': self.model_id.id,
                    'trigger': 'on_write',
                    'trigger_field_ids': [self.field_id.id],
                })
                code_line = []
                if self.field_id.ttype == 'selection':
                    # If the field is a selection field
                    code_line.append((0, 0, {
                        'name': f'User notification on {self.field_id.field_description} change of {self.model_id.name}',
                        'model_id': self.model_id.id,
                        'state': 'code',
                        'code': f"""for rec in records:\n  if rec.{self.field_id.name} in {self.state_ids.mapped('key')}:\n    state_val = dict(rec._fields['{self.field_id.name}'].selection).get(rec.state)\n    env.user.sudo().generate_notification_on_state_change(notification_config_id={self.id}, record=rec, state=state_val)"""
                        }))
                elif self.field_id.ttype == 'many2one':
                    # If the field is a Many2one field
                    code_line.append((0, 0, {
                        'name': f'User notification on {self.field_id.field_description} change of {self.model_id.name}',
                        'model_id': self.model_id.id,
                        'state': 'code',
                        'code': f"""for rec in records:\n  if rec.{self.field_id.name}.name in {self.state_ids.mapped('name')}:\n    state_val = rec.{self.field_id.name}.name\n    env.user.sudo().generate_notification_on_state_change(notification_config_id={self.id}, record=rec, state=state_val)"""

                    }))

                on_change_action_id.action_server_ids = code_line
                if on_change_action_id:
                    self.on_change_action_id = on_change_action_id.id
            else:
                x = self.on_change_action_id.write({
                    'active': True,
                    'is_notify_action': True,
                    'name': f'User notification on {self.field_id.field_description} change of {self.model_id.name}',
                    'model_id': self.model_id.id,
                    'trigger': 'on_write',
                    'trigger_field_ids': [self.field_id.id],
                })
                self.on_change_action_id.action_server_ids.model_id = self.model_id.id
                self.on_change_action_id.action_server_ids.state = 'code'
                if self.field_id.ttype == 'selection':
                    self.on_change_action_id.action_server_ids.code = f"""for rec in records:\n  if rec.{self.field_id.name} in {self.state_ids.mapped('key')}:\n    state_val = dict(rec._fields['{self.field_id.name}'].selection).get(rec.state)\n    env.user.sudo().generate_notification_on_state_change(notification_config_id={self.id}, record=rec, state=state_val)"""
                elif self.field_id.ttype == 'many2one':
                    self.on_change_action_id.action_server_ids.code = f"""for rec in records:\n  if rec.{self.field_id.name}.name in {self.state_ids.mapped('name')}:\n    state_val = rec.{self.field_id.name}.name\n    env.user.sudo().generate_notification_on_state_change(notification_config_id={self.id}, record=rec, state=state_val)"""

        else:
            if self.on_change_action_id:
                self.on_change_action_id.write({'active': False})

    @api.onchange('model_id', 'on_state_change', 'field_id')
    def onchange_get_state(self):
        """This method create a state field value based on selected field"""
        for notify in self:
            notify.state_ids = False
            states = self.env['state.value'].search([('field_id', '=', notify.field_id.id)])
            if notify.model_id and notify.on_state_change and notify.field_id:
                if not states:
                    if self.field_id.selection_ids:
                        for option in self.field_id.selection_ids:
                            vals = {
                                'key': option.value,
                                'name': option.name,
                                'field_id': notify.field_id.id,
                            }
                            self.env['state.value'].create(vals)
                    else:
                        model = self.field_id.relation
                        if model:
                            a = self.env[model].search([(True,'=',True)])
                            for option in a:
                                vals = {
                                    'key': option.id,
                                    'name': option.name,
                                    'field_id': notify.field_id.id,
                                }
                                self.env['state.value'].create(vals)








