from odoo import models, fields, api
from datetime import datetime, timedelta

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    no_recent_delivery = fields.Boolean(
        string='No Recent Delivery',
        compute='_compute_no_recent_delivery',
        store=True,
    )

    @api.depends('product_id', 'date', 'picking_id.state', 'picking_id.picking_type_id.code', 'picking_id.move_line_ids', 'picking_id.move_line_ids.product_id', 'picking_id.move_line_ids.date')
    def _compute_no_recent_delivery(self):
        seven_days_ago = datetime.now() - timedelta(days=7)
        # Find move lines from done outgoing deliveries in the last 7 days
        recent_move_lines = self.env['stock.move.line'].search([
            ('picking_id.state', '=', 'done'),
            ('picking_id.picking_type_id.code', '=', 'outgoing'),
            ('date', '>=', seven_days_ago),
        ])
        products_with_recent_moves = recent_move_lines.mapped('product_id')

        for product in products_with_recent_moves:
            print('produdct : ',product)

        for move_line in self:
            if (move_line.picking_id and
                move_line.picking_id.state == 'done' and
                move_line.picking_id.picking_type_id.code == 'outgoing'):
                # Check all products in the same delivery
                delivery_products = move_line.picking_id.move_line_ids.mapped('product_id')
                has_recent_move = any(product in products_with_recent_moves for product in delivery_products)
                print('delivery_products : ',delivery_products)
                print('has_recent_move : ', has_recent_move)
                move_line.no_recent_delivery = not has_recent_move
            else:
                move_line.no_recent_delivery = False

    @api.model
    def create(self, vals):
        # Create the new record
        move_line = super(StockMoveLine, self).create(vals)
        # If the new move line is in a done outgoing delivery, recompute no_recent_delivery
        if (move_line.picking_id and
            move_line.picking_id.state == 'done' and
            move_line.picking_id.picking_type_id.code == 'outgoing'):
            self._recompute_no_recent_delivery_for_products(move_line.product_id)
        return move_line

    def write(self, vals):
        # Update the record
        result = super(StockMoveLine, self).write(vals)
        # If relevant fields are updated, recompute
        if any(key in vals for key in ['product_id', 'date', 'picking_id']) or \
           (self.picking_id and 'state' in vals.get('picking_id', {})):
            products = self.mapped('product_id')
            self._recompute_no_recent_delivery_for_products(products)
        return result

    def _recompute_no_recent_delivery_for_products(self, products):
        # Find all move lines for the given products or their deliveries, only for outgoing
        affected_move_lines = self.env['stock.move.line'].search([
            ('picking_id.state', '=', 'done'),
            ('picking_id.picking_type_id.code', '=', 'outgoing'),
            '|',
            ('product_id', 'in', products.ids),
            ('picking_id.move_line_ids.product_id', 'in', products.ids),
        ])
        # Recompute no_recent_delivery for these records
        affected_move_lines._compute_no_recent_delivery()

    def cron_recompute_no_recent_delivery(self):
        # Recompute for all done outgoing move lines
        move_lines = self.env['stock.move.line'].search([
            ('picking_id.state', '=', 'done'),
            ('picking_id.picking_type_id.code', '=', 'outgoing'),
        ])
        move_lines._compute_no_recent_delivery()