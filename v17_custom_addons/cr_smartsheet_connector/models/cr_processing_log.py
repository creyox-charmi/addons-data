# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields

class DataProcessingLog(models.Model):
    _name = 'cr.processing.log'
    _description = 'Log of data processing operations'

    cr_conf_id = fields.Many2one('cr.smartsheet.config', string='SmartSheet Configuration', required=True)
    cr_record_count = fields.Integer('Number of Records', required=True)
    cr_status = fields.Selection([
        ('success', 'Success'),
        ('failure', 'Failure')
    ], default='success', required=True)
    cr_error_message = fields.Text('Error Message')
    cr_timestamp = fields.Char('Timestamp')
    cr_initiated_at = fields.Char('Initiated At ')
    cr_message = fields.Char('Message')

    def _log_data_processing(self, cr_conf_id, record_count,cr_message, status, timespan, initiated_at, error_message=''):
        """Logs data processing operations into the DataProcessingLog model."""
        self.env['cr.data.processing.log'].sudo().create({
            'cr_conf_id': cr_conf_id,
            'cr_message':cr_message,
            'cr_record_count': record_count,
            'cr_status': status,
            'cr_error_message': error_message,
            'cr_timestamp': timespan,
            'cr_initiated_at': initiated_at,
        })