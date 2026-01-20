from odoo import models, fields, api
from datetime import datetime


class BigCommerceImportProgressWizard(models.TransientModel):
    _name = 'bigcommerce.import.progress.wizard'
    _description = 'BigCommerce Import Progress'

    store_id = fields.Many2one('bigcommerce.store', string='Store', required=True)

    import_type = fields.Selection([
        ('customer', 'Customer'),
        ('order', 'Order'),
        ('product', 'Product'),
        ('address', 'Address'),  # Add this line
    ], string='Import Type', required=True)

    status = fields.Char(string='Status', compute='_compute_progress')
    total_processed = fields.Integer(string='Total Processed', compute='_compute_progress')
    created_count = fields.Integer(string='Created', compute='_compute_progress')
    updated_count = fields.Integer(string='Skipped', compute='_compute_progress')  # Changed label for products
    progress_percentage = fields.Float(string='Progress %', compute='_compute_progress')
    elapsed_time = fields.Char(string='Elapsed Time', compute='_compute_progress')
    error_message = fields.Text(string='Error', compute='_compute_progress')


    @api.depends('store_id', 'import_type')
    def _compute_progress(self):
        for record in self:
            prefix = f'bigcommerce.{record.import_type}.import'

            status = self.env['ir.config_parameter'].sudo().get_param(
                f'{prefix}.active.{record.store_id.id}', 'false'
            )

            if status == 'true':
                record.status = 'In Progress'
            elif status == 'completed':
                record.status = 'Completed'
            elif status == 'failed':
                record.status = 'Failed'
            else:
                record.status = 'Not Started'

            record.total_processed = int(self.env['ir.config_parameter'].sudo().get_param(
                f'{prefix}.total.{record.store_id.id}', '0'
            ))

            record.created_count = int(self.env['ir.config_parameter'].sudo().get_param(
                f'{prefix}.created.{record.store_id.id}', '0'
            ))

            record.updated_count = int(self.env['ir.config_parameter'].sudo().get_param(
                f'{prefix}.updated.{record.store_id.id}', '0'
            ))

            # Calculate progress (estimate based on processed count)
            if record.total_processed > 0:
                record.progress_percentage = min(99.0, (record.total_processed / 100.0))
            else:
                record.progress_percentage = 0.0

            if status == 'completed':
                record.progress_percentage = 100.0

            # Calculate elapsed time
            start_time_str = self.env['ir.config_parameter'].sudo().get_param(
                f'{prefix}.start_time.{record.store_id.id}', ''
            )

            if start_time_str:
                start_time = fields.Datetime.from_string(start_time_str)

                if status == 'completed':
                    end_time_str = self.env['ir.config_parameter'].sudo().get_param(
                        f'{prefix}.end_time.{record.store_id.id}', str(fields.Datetime.now())
                    )
                    end_time = fields.Datetime.from_string(end_time_str)
                else:
                    end_time = fields.Datetime.now()

                elapsed = end_time - start_time
                minutes, seconds = divmod(elapsed.total_seconds(), 60)
                record.elapsed_time = f"{int(minutes)}m {int(seconds)}s"
            else:
                record.elapsed_time = "0m 0s"

            # Get error message if failed
            if status == 'failed':
                record.error_message = self.env['ir.config_parameter'].sudo().get_param(
                    f'{prefix}.error.{record.store_id.id}', 'Unknown error'
                )
            else:
                record.error_message = ''

    def action_refresh(self):
        """Refresh progress data."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bigcommerce.import.progress.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_close(self):
        """Close the wizard."""
        return {'type': 'ir.actions.act_window_close'}