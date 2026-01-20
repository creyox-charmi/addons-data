# controllers/main.py

from odoo import http
from odoo.http import request
import json


class BigCommerceImportController(http.Controller):

    @http.route('/bigcommerce/import/progress', type='json', auth='user')
    def get_import_progress(self, store_id, import_type):
        """Get real-time import progress."""
        prefix = f'bigcommerce.{import_type}.import'

        status = request.env['ir.config_parameter'].sudo().get_param(
            f'{prefix}.active.{store_id}', 'false'
        )

        total = int(request.env['ir.config_parameter'].sudo().get_param(
            f'{prefix}.total.{store_id}', '0'
        ))

        # ADD THIS: Get total expected count
        total_expected = int(request.env['ir.config_parameter'].sudo().get_param(
            f'{prefix}.total_expected.{store_id}', '0'
        ))

        created = int(request.env['ir.config_parameter'].sudo().get_param(
            f'{prefix}.created.{store_id}', '0'
        ))

        updated = int(request.env['ir.config_parameter'].sudo().get_param(
            f'{prefix}.updated.{store_id}', '0'
        ))

        start_time_str = request.env['ir.config_parameter'].sudo().get_param(
            f'{prefix}.start_time.{store_id}', ''
        )

        error_msg = ''
        if status == 'failed':
            error_msg = request.env['ir.config_parameter'].sudo().get_param(
                f'{prefix}.error.{store_id}', 'Unknown error'
            )

        elapsed_time = ''
        if start_time_str:
            from odoo import fields
            from datetime import datetime
            start_time = fields.Datetime.from_string(start_time_str)

            if status == 'completed':
                end_time_str = request.env['ir.config_parameter'].sudo().get_param(
                    f'{prefix}.end_time.{store_id}', str(fields.Datetime.now())
                )
                end_time = fields.Datetime.from_string(end_time_str)
            else:
                end_time = fields.Datetime.now()

            elapsed = end_time - start_time
            minutes, seconds = divmod(elapsed.total_seconds(), 60)
            elapsed_time = f"{int(minutes)}m {int(seconds)}s"

        return {
            'status': status,
            'total_processed': total,
            'total_expected': total_expected,  # ADD THIS LINE
            'created': created,
            'updated': updated,
            'elapsed_time': elapsed_time,
            'error_message': error_msg,
        }