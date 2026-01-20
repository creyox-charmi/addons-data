from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
import logging
import json

_logger = logging.getLogger(__name__)


class CrGanttViewProject(models.Model):
    _inherit = 'project.project'

    def ks_compute_json_data_project_task(self):
        print('firsttttt')
        for rec in self:
            ks_project_task_json = []
            ks_all_task_obj = self.env['project.task'].search([('project_id', '=', rec.id)])
            for ks_task in ks_all_task_obj:
                if ks_task.user_ids:
                    for ks_user in range(0, len(ks_task.user_ids)):
                        ks_project_task_json.append(
                            {
                                'id': 'task_' + str(ks_task.id),
                                'ks_task_start_date': str(ks_task.ks_start_datetime),
                                'ks_task_end_date': str(ks_task.ks_end_datetime),
                                'ks_task_id': 'task_' + str(ks_task.id),
                                'ks_task_name': ks_task.name,
                                'ks_task_color': ks_task.ks_color,
                                'ks_task_model': 'project.task',
                                'parent_id': 'task_' + str(ks_task.parent_id.id) if ks_task.parent_id.id else False,
                                'project_id': [ks_task.project_id.id, ks_task.project_id.name],
                                'partner_id': [ks_task.partner_id.id, ks_task.partner_id.name],
                                'company_id': [ks_task.company_id.id, ks_task.company_id.name],
                                'mark_as_important': ks_task.priority,
                                'ks_enable_task_duration': ks_task.ks_enable_task_duration,
                                'deadline': str(ks_task.date_deadline) if ks_task.date_deadline else False,
                                'progress': ks_task.progress,
                                'ks_allow_subtask': ks_task.ks_allow_subtask,
                                'ks_allow_parent_task': ks_task.ks_allow_subtask,
                                'ks_schedule_mode': ks_task.ks_schedule_mode,
                                'constraint_type': ks_task.ks_constraint_task_type,
                                'constraint_date': str(ks_task.ks_constraint_task_date) if ks_task.ks_constraint_task_date else False,
                                'stage_id': [ks_task.stage_id.id, ks_task.stage_id.name],
                                'unscheduled': ks_task.ks_task_unschedule,
                                'ks_owner_task': [ks_task.user_ids[ks_user].id, ks_task.user_ids[ks_user].name] if ks_task.user_ids else False,
                                'resource_working_hours': ks_task.ks_resource_hours_per_day,
                                'type': ks_task.ks_task_type,
                                'ks_resource_hours_available': ks_task.ks_resource_hours_available,
                                'ks_task_link_json': ks_task.ks_task_link_json,
                                'planned_hours': ks_task.allocated_hours,
                                'amount_cost':ks_task.amount_cost,
                                'amount_target':ks_task.amount_target,
                                'price_subtotal':ks_task.price_subtotal,
                                'is_show_pr': 1 if ks_task.parent_id else 0,
                                'percentage': ks_task.ks_compute_percentage(),
                            }
                        )
                else:
                    ks_project_task_json.append(
                        {
                            'id': 'task_' + str(ks_task.id),
                            'ks_task_start_date': str(ks_task.ks_start_datetime),
                            'ks_task_end_date': str(ks_task.ks_end_datetime),
                            'ks_task_id': 'task_' + str(ks_task.id),
                            'ks_task_name': ks_task.name,
                            'ks_task_color': ks_task.ks_color,
                            'ks_task_model': 'project.task',
                            'parent_id': 'task_' + str(ks_task.parent_id.id) if ks_task.parent_id.id else False,
                            'project_id': [ks_task.project_id.id, ks_task.project_id.name],
                            'partner_id': [ks_task.partner_id.id, ks_task.partner_id.name],
                            'company_id': [ks_task.company_id.id, ks_task.company_id.name],
                            'mark_as_important': ks_task.priority,
                            'ks_enable_task_duration': ks_task.ks_enable_task_duration,
                            'deadline': str(ks_task.date_deadline) if ks_task.date_deadline else False,
                            'progress': ks_task.progress,
                            'ks_allow_subtask': ks_task.ks_allow_subtask,
                            'ks_allow_parent_task': ks_task.ks_allow_subtask,
                            'ks_schedule_mode': ks_task.ks_schedule_mode,
                            'constraint_type': ks_task.ks_constraint_task_type,
                            'constraint_date': str(
                                ks_task.ks_constraint_task_date) if ks_task.ks_constraint_task_date else False,
                            'stage_id': [ks_task.stage_id.id, ks_task.stage_id.name],
                            'unscheduled': ks_task.ks_task_unschedule,
                            'ks_owner_task': [],
                            'resource_working_hours': ks_task.ks_resource_hours_per_day,
                            'type': ks_task.ks_task_type,
                            'ks_resource_hours_available': ks_task.ks_resource_hours_available,
                            'ks_task_link_json': ks_task.ks_task_link_json,
                            'planned_hours': ks_task.allocated_hours,
                            'amount_cost': ks_task.amount_cost,
                            'amount_target': ks_task.amount_target,
                            'price_subtotal': ks_task.price_subtotal,
                            'is_show_pr': 1 if ks_task.parent_id else 0,
                            'percentage': ks_task.ks_compute_percentage(),
                        }
                    )
            rec.ks_project_task_json = json.dumps(ks_project_task_json)

    def ks_compute_json_data_project_task_link(self):
        print('second')
        for rec in self:
            ks_project_task_json = []
            ks_all_task_obj = self.env['project.task'].search([('project_id', '=', rec.id)])
            for ks_task in ks_all_task_obj:
                for ks_user in range(0,len(ks_task.user_ids)):
                    ks_project_task_json.append(
                        {
                            'id': 'task_' + str(ks_task.id),
                            'ks_task_start_date': str(ks_task.ks_start_datetime),
                            'ks_task_end_date': str(ks_task.ks_end_datetime),
                            'ks_task_id': 'task_' + str(ks_task.id),
                            'ks_task_name': ks_task.name,
                            'ks_task_color': ks_task.ks_color,
                            'ks_task_model': 'project.task',
                            'parent_id': 'task_' + str(ks_task.parent_id.id) if ks_task.parent_id.id else False,
                            'project_id': ks_task.project_id.id,
                            'mark_as_important': ks_task.priority,
                            'deadline': str(ks_task.date_deadline) if ks_task.date_deadline else False,
                            'progress': ks_task.progress,
                            'ks_allow_subtask': ks_task.ks_allow_subtask,
                            'ks_allow_parent_task': ks_task.ks_allow_subtask,
                            'ks_schedule_mode': ks_task.ks_schedule_mode,
                            'constraint_type': ks_task.ks_constraint_task_type,
                            'constraint_date': str(
                                ks_task.ks_constraint_task_date) if ks_task.ks_constraint_task_date else False,
                            'stage_id': [ks_task.stage_id.id, ks_task.stage_id.name],
                            'unscheduled': ks_task.ks_task_unschedule,
                            'ks_owner_task': [ks_task.user_ids[ks_user].id, ks_task.user_ids[ks_user].name] if ks_task.user_ids else False,
                            'resource_working_hours': ks_task.ks_resource_hours_per_day,
                            'type': ks_task.ks_task_type,
                            'ks_resource_hours_available': ks_task.ks_resource_hours_available,
                            'amount_cost': ks_task.amount_cost,
                            'amount_target': ks_task.amount_target,
                            'price_subtotal': ks_task.price_subtotal,
                            'is_show_pr': 1 if ks_task.parent_id else 0,
                            'percentage': ks_task.ks_compute_percentage(),
                        }
                    )
            rec.ks_project_task_json = json.dumps(ks_project_task_json)

