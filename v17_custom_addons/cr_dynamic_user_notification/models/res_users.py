# -*- coding: utf-8 -*-
from odoo import _, api, exceptions, fields, models
from odoo.addons.bus.models.bus import channel_with_db, json_dump


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.depends("create_date")
    def _compute_channel_names(self):
        for record in self:
            record.notify_success_channel_name = json_dump(channel_with_db(self.env.cr.dbname, record.partner_id))
            record.notify_danger_channel_name = json_dump(channel_with_db(self.env.cr.dbname, record.partner_id))
            record.notify_warning_channel_name = json_dump(channel_with_db(self.env.cr.dbname, record.partner_id))
            record.notify_info_channel_name = json_dump(channel_with_db(self.env.cr.dbname, record.partner_id))
            record.notify_default_channel_name = json_dump(channel_with_db(self.env.cr.dbname, record.partner_id))

    notify_success_channel_name = fields.Char(compute="_compute_channel_names")
    notify_danger_channel_name = fields.Char(compute="_compute_channel_names")
    notify_warning_channel_name = fields.Char(compute="_compute_channel_names")
    notify_info_channel_name = fields.Char(compute="_compute_channel_names")
    notify_default_channel_name = fields.Char(compute="_compute_channel_names")

    def _notification_channel(self, type='default', message='Default Message', title=None, sticky=False, target=None):
        """This method generates a notification"""
        if not self.env.user._is_admin() and any(user.id != self.env.uid for user in self):
            raise exceptions.UserError(_("Sending a notification to another user is forbidden."))
        if not target:
            target = self.env.user.partner_id
        bus_message = {
            "type": type,
            "message": message,
            "title": title,
            "sticky": sticky,
        }
        notifications = [[partner, "web.notify", [bus_message]] for partner in target]
        self.env["bus.bus"]._sendmany(notifications)

    def generate_notification_on_record_create(self, notification_config_id=False, record=False):
        """This method prepares required data to generate the notification when record is created for selected model in
            automated action"""
        if notification_config_id:
            notification_id = self.env['notification.config'].sudo().browse(notification_config_id)
            name_field = self.env['ir.model.fields'].search(
                [('model_id', '=', notification_id.model_id.id), ('name', '=', 'name')], limit=1)
            name = ''
            if name_field:
                name = record.name
            if notification_id:
                message = f'{notification_id.model_id.name} is created {name}'
                type = notification_id.notification_type
                title = notification_id.name
                sticky = notification_id.is_sticky
                if notification_id.model_id.name == 'Lead/Opportunity' or notification_id.model_id.name == 'Task':
                    for field in notification_id.model_id.field_id:
                        if field.name == 'user_id':
                            target = record.user_id.mapped('partner_id')
                        if field.name == 'user_ids':
                            target = record.user_ids.mapped('partner_id')
                else:
                    target = notification_id.notify_user_ids.mapped('partner_id')
                self._notification_channel(type=type, message=message, title=title, sticky=sticky, target=target)

    def generate_notification_on_state_change(self, notification_config_id=False, record=False, state=False):
        """This method prepares required data to generate the notification when state change of selected field in
            automated action"""
        if notification_config_id:
            notification_id = self.env['notification.config'].sudo().browse(notification_config_id)
            name_field = self.env['ir.model.fields'].search(
                [('model_id', '=', notification_id.model_id.id), ('name', '=', 'name')], limit=1)
            name = ''
            if name_field:
                name = record.name
            if notification_id:
                message = f'{notification_id.model_id.name} {name} status updated to {state}'
                type = notification_id.notification_type
                title = notification_id.name
                sticky = notification_id.is_sticky
                if notification_id.model_id.name == 'Lead/Opportunity' or notification_id.model_id.name == 'Task':
                    for field in notification_id.model_id.field_id:
                        if field.name == 'user_id':
                            target = record.user_id.mapped('partner_id')
                        if field.name == 'user_ids':
                            target = record.user_ids.mapped('partner_id')
                else:
                    target = notification_id.notify_user_ids.mapped('partner_id')
                self._notification_channel(type=type, message=message, title=title, sticky=sticky, target=target)
