from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class ProductRejectionwizard(models.TransientModel):
    _name = "product.rejection.wiz"
    _description = "rejection wiz"

    reason_reject = fields.Char(string="Reason for Rejection", required=True)
    reject_by = fields.Char(string="Rejected By", required=True, default=lambda self: self.env.user.name, readonly=True)
    reject_on = fields.Datetime(string="Rejected on", required=True, default=datetime.now(), readonly=True)
    logged_in_admin_job_level = fields.Char(string="Logged in user job level")


    def action_save_reject_button(self):
        active_id = self._context.get('active_id')
        product_temp_id = self.env['product.template'].sudo().browse(active_id)

        job_position_product_temp_id = self.env['hr.employee'].search([('user_id', '=', self._uid)], )
        workflow_id = self.env['product.approval.workflow.master'].search([('active_status', '=', True)], limit=1)
        for line in workflow_id.approval_line_ids:
            if line.job_position_id == job_position_product_temp_id.job_id:
                self.logged_in_admin_job_level = line.approval_level
                break

        if len(workflow_id.approval_line_ids) == 1:
            for line in workflow_id.approval_line_ids:
                if line.approval_level == self.logged_in_admin_job_level:
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if not last_history:
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]
                        })
                    else:
                        raise ValidationError(_("You're not authorised person."))
                else:
                    raise ValidationError(_("You're not authorised person."))

        elif len(workflow_id.approval_line_ids) == 2:
            level_first = workflow_id.approval_line_ids.filtered(lambda x: x.approval_level == 'first')
            level_second = workflow_id.approval_line_ids.filtered(lambda x: x.approval_level == 'second')
            level_third = workflow_id.approval_line_ids.filtered(lambda x: x.approval_level == 'third')

            if level_first and level_second and not level_third:
                if level_first.approval_level == 'first' and self.logged_in_admin_job_level == 'first':
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if not last_history:
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # to delete many 2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                    elif last_history and last_history.approved_rejected == 'rejected':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # to delete many 2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]

                    else:
                        raise ValidationError(_("You're not authorised person."))
                elif level_second.approval_level == 'second' and self.logged_in_admin_job_level == 'second':
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if last_history.level_admin_user == 'first' and last_history.approved_rejected == 'approved':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # to delete many 2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                    else:
                        raise ValidationError(_("You're not authorised person."))
            elif level_second and level_third and not level_first:

                if level_second.approval_level == 'second' and self.logged_in_admin_job_level == 'second':
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if not last_history:
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # to delete many 2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                    elif last_history and last_history.approved_rejected == 'rejected':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # to delete many 2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]

                    else:
                        raise ValidationError(_("You're not authorised person."))
                elif level_third.approval_level == 'third' and self.logged_in_admin_job_level == 'third':
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if last_history.level_admin_user == 'second' and last_history.approved_rejected == 'approved':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # to delete many 2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                    else:
                        raise ValidationError(_("You're not authorised person."))
            elif level_third and level_first and not level_second:
                if level_first.approval_level == 'first' and self.logged_in_admin_job_level == 'first':
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if not last_history:
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                    elif last_history and last_history.approved_rejected == 'rejected':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # to delete many 2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]

                    else:
                        raise ValidationError(_("You're not authorised person."))
                elif level_third.approval_level == 'third' and self.logged_in_admin_job_level == 'third':
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if last_history.level_admin_user == 'first' and last_history.approved_rejected == 'approved':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                    else:
                        raise ValidationError(_("You're not authorised person."))

        else:
            for lines in workflow_id.approval_line_ids:
                if lines.approval_level == 'first' and self.logged_in_admin_job_level == 'first':
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if not last_history:
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # delete many2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]

                        break
                    elif last_history and last_history.approved_rejected == 'rejected':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # delete many2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                        break

                    else:
                        raise ValidationError(_("You're not authorised person."))

                elif lines.approval_level == 'second' and self.logged_in_admin_job_level == 'second':

                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if last_history.level_admin_user == 'first' and last_history.approved_rejected == "approved":
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # delete many2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                        break
                    elif last_history and last_history.approved_rejected == 'rejected':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # delete many2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                        break

                    else:
                        raise ValidationError(_("You're not authorised person."))

                elif lines.approval_level == 'third' and self.logged_in_admin_job_level == 'third':
                    last_history = self.env['product.approval.history'].search([('product_approval_hist_id', '=', product_temp_id.id)], order='create_date desc', limit=1)
                    if last_history.level_admin_user == 'second' and last_history.approved_rejected == 'approved':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # delete many2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                        break
                    elif last_history and last_history.approved_rejected == 'rejected':
                        product_temp_id.write({
                            'state': 'reject',
                            'active': False,
                            'related_users_ids': [(5, 0, 0)],
                            'product_approval_history_ids': [(0, 0, {
                                'approved_by': self.reject_by,
                                'approved_on': self.reject_on,
                                'approval_reason': self.reason_reject,
                                'approved_rejected': "rejected",
                                'level_admin_user': self.logged_in_admin_job_level,
                            })]

                        })
                        # delete many2 many
                        # product_temp_id.related_users_ids = [(5, 0, 0)]
                        break

                    else:
                        raise ValidationError(_("You're not authorised person."))
                