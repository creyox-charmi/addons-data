# models/mrp_bom_automated_flow.py
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class MrpBomAutomatedFlowProcessor(models.TransientModel):
    _name = 'mrp.bom.automated.flow.processor'
    _description = 'Automated Flow Processor for EVR BOM Lines'

    @api.model
    def process_line(self, root_bom, bom_line, branch_record, accumulated_qty=None):
        """
        Main entry point to process a BOM line
        branch_record: mrp.bom.line.branch record to store values
        accumulated_qty: The quantity considering parent BOM multipliers
        """

        if not branch_record or not branch_record.location_id:
            return

        if accumulated_qty is None:
            accumulated_qty = float(bom_line.product_qty or 1.0)

        self._process_cfe_flow(root_bom, bom_line, branch_record, accumulated_qty)
        self._process_regular_flow(root_bom, bom_line, branch_record, accumulated_qty)

    def _process_cfe_flow(self, root_bom, bom_line, branch_record, accumulated_qty):
        """Process CFE flow and store in branch_record"""

        # cfe_qty_per_unit = float(bom_line.cfe_quantity or 0)
        # cfe_qty = cfe_qty_per_unit * accumulated_qty

        cfe_qty = float(bom_line.cfe_quantity or 0)

        if cfe_qty <= 0:
            return

        if branch_record.used == cfe_qty:
            return

        customer = root_bom.project_id.partner_id if root_bom.project_id else False
        if not customer:
            return

        branch_location = branch_record.location_id

        # 1. Update Transferred CFE
        transferred_cfe = self._get_stock_in_location(bom_line.product_id, branch_location, owner=customer)
        branch_record.transferred_cfe = transferred_cfe

        # 2. Update To Transfer CFE
        to_transfer_cfe = self._get_pending_moves_to_location(bom_line.product_id, branch_location, owner=customer)

        # 3. Check and create/update internal transfers
        needed_transfer = cfe_qty - transferred_cfe - to_transfer_cfe

        if needed_transfer > 0:
            free_stock = self._get_free_stock_owned_by(bom_line.product_id, customer)
            transfer_qty = min(needed_transfer, free_stock)

            if transfer_qty > 0:
                self._create_or_update_internal_transfer(
                    bom_line.product_id, branch_location, transfer_qty, owner=customer, is_cfe=True
                )
                to_transfer_cfe += transfer_qty

        branch_record.to_transfer_cfe = to_transfer_cfe

        # 4. Update Ordered CFE
        ordered_cfe = self._get_ordered_qty(bom_line, branch_record, is_cfe=True)
        branch_record.ordered_cfe = ordered_cfe

        # 5. Update To Order CFE
        to_order_cfe = cfe_qty - transferred_cfe - to_transfer_cfe - ordered_cfe
        branch_record.to_order_cfe = max(to_order_cfe, 0)

        # 6. Create/update CFE PO
        if to_order_cfe > 0:
            self._create_or_update_cfe_po(root_bom, bom_line, branch_record, to_order_cfe)
        elif to_order_cfe <= 0:
            self._remove_cfe_po_line(bom_line, branch_record)

    def _process_regular_flow(self, root_bom, bom_line, branch_record, accumulated_qty):
        """Process regular flow and store in branch_record"""

        cfe_qty_per_unit = float(bom_line.cfe_quantity or 0)
        total_qty = accumulated_qty
        cfe_qty = cfe_qty_per_unit * accumulated_qty
        x = total_qty - cfe_qty

        if x <= 0:
            return

        if branch_record.used == x:
            return

        branch_location = branch_record.location_id

        # 1. Update Transferred
        transferred = self._get_stock_in_location(bom_line.product_id, branch_location, owner=False)
        branch_record.transferred = transferred

        # 2. Update To Transfer
        to_transfer = self._get_pending_moves_to_location(bom_line.product_id, branch_location, owner=False)

        # 3. Check and create/update internal transfers
        needed_transfer = x - transferred - to_transfer

        if needed_transfer > 0:
            free_stock = self._get_free_stock_owned_by(bom_line.product_id, owner=False)
            transfer_qty = min(needed_transfer, free_stock)

            if transfer_qty > 0:
                self._create_or_update_internal_transfer(
                    bom_line.product_id, branch_location, transfer_qty, owner=False, is_cfe=False
                )
                to_transfer += transfer_qty

        branch_record.to_transfer = to_transfer

        # 4. Update Ordered
        ordered = self._get_ordered_qty(bom_line, branch_record, is_cfe=False)
        branch_record.ordered = ordered

        # 5. Update To Order
        to_order = x - transferred - to_transfer - ordered
        branch_record.to_order = max(to_order, 0)

        # 6. Create/update regular PO
        if to_order > 0:
            self._create_or_update_regular_po(root_bom, bom_line, branch_record, to_order)
        elif to_order <= 0:
            self._remove_regular_po_line(bom_line, branch_record)

    def _get_stock_in_location(self, product, location, owner=False):
        """Get available stock in specific location"""
        domain = [
            ('product_id', '=', product.id),
            ('location_id', '=', location.id),
        ]

        if owner:
            domain.append(('owner_id', '=', owner.id))
        else:
            domain.append(('owner_id', '=', False))

        quants = self.env['stock.quant'].search(domain)
        return sum(quants.mapped('quantity'))

    def _get_pending_moves_to_location(self, product, location, owner=False):
        """Get quantity in pending moves to location"""
        domain = [
            ('product_id', '=', product.id),
            ('location_dest_id', '=', location.id),
            ('state', 'not in', ['done', 'cancel']),
        ]

        if owner:
            domain.append(('restrict_partner_id', '=', owner.id))
        else:
            domain.append(('restrict_partner_id', '=', False))

        # moves = self.env['stock.move'].search(domain)
        moves = self.env['stock.move'].search(domain)
        # return sum(moves.mapped('product_uom_qty'))
        return sum(moves.mapped('quantity'))

    def _get_free_stock_owned_by(self, product, owner=False):
        """Get free stock in free locations"""
        free_locations = self.env['stock.location'].search([
            ('location_category', '=', 'free'),
            ('usage', '=', 'internal')
        ])

        if not free_locations:
            return 0.0

        domain = [
            ('product_id', '=', product.id),
            ('location_id', 'in', free_locations.ids),
        ]

        if owner:
            domain.append(('owner_id', '=', owner.id))
        else:
            domain.append(('owner_id', '=', False))

        quants = self.env['stock.quant'].search(domain)
        return sum(quants.mapped('quantity'))

    def _create_or_update_internal_transfer(self, product, dest_location, qty, owner=False, is_cfe=False):
        """Create or update internal transfer"""

        # Find existing pending transfer
        domain = [
            ('product_id', '=', product.id),
            ('location_dest_id', '=', dest_location.id),
            ('state', 'in', ['draft', 'waiting', 'confirmed', 'assigned']),
        ]

        if owner:
            domain.append(('restrict_partner_id', '=', owner.id))

        existing_move = self.env['stock.move'].search(domain, limit=1)

        if existing_move:
            existing_move.product_uom_qty = qty
        else:
            free_locations = self.env['stock.location'].search([
                ('location_category', '=', 'free'),
                ('usage', '=', 'internal')
            ], limit=1)

            if not free_locations:
                return

            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('warehouse_id.company_id', '=', self.env.company.id)
            ], limit=1)

            picking_vals = {
                'picking_type_id': picking_type.id,
                'location_id': free_locations[0].id,
                'location_dest_id': dest_location.id,
                'origin': f'Auto Transfer - {product.display_name}',
            }

            if owner:
                picking_vals['owner_id'] = owner.id

            picking = self.env['stock.picking'].create(picking_vals)

            move_vals = {
                'name': product.display_name,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': product.uom_id.id,
                'location_id': free_locations[0].id,
                'location_dest_id': dest_location.id,
                'picking_id': picking.id,
            }

            if owner:
                move_vals['restrict_partner_id'] = owner.id

            self.env['stock.move'].create(move_vals)
            picking.action_confirm()

    def _get_ordered_qty(self, bom_line, branch_record, is_cfe=False):
        """Get ordered quantity from approved POs"""
        domain = [
            ('product_id', '=', bom_line.product_id.id),
            ('bom_line_ids', 'in', [bom_line.id]),
            ('bom_id', '=', branch_record.bom_id.id),
            ('order_id.state', 'in', ['purchase', 'done']),
        ]

        if is_cfe:
            domain.append(('order_id.cfe', '=', True))
        else:
            domain.append(('order_id.cfe', '=', False))

        po_lines = self.env['purchase.order.line'].search(domain)
        return sum(po_lines.mapped('product_qty'))

    def _create_or_update_cfe_po(self, root_bom, bom_line, branch_record, qty):
        """Create or update CFE PO"""
        customer = root_bom.project_id.partner_id
        if not customer:
            return

        existing_po = self.env['purchase.order'].search([
            ('partner_id', '=', customer.id),
            ('cfe', '=', True),
            ('state', '=', 'draft'),
            ('bom_id', '=', root_bom.id),
        ], limit=1)

        if not existing_po:
            existing_po = self.env['purchase.order'].create({
                'partner_id': customer.id,
                'cfe': True,
                'cfe_project_location_id': branch_record.location_id.id,
                'bom_id': root_bom.id,
                'origin': f'Auto CFE - {root_bom.display_name}',
            })

        existing_line = existing_po.order_line.filtered(
            lambda l: l.product_id == bom_line.product_id and bom_line.id in l.bom_line_ids.ids
        )

        if existing_line:
            existing_line.product_qty = qty
        else:
            self.env['purchase.order.line'].create({
                'order_id': existing_po.id,
                'product_id': bom_line.product_id.id,
                'product_qty': qty,
                'product_uom': bom_line.product_id.uom_po_id.id,
                'price_unit': 0.0,
                'name': f'CFE - {bom_line.product_id.display_name}',
                'bom_line_ids': [(4, bom_line.id)],
                'bom_id': root_bom.id,
            })

    def _create_or_update_regular_po(self, root_bom, bom_line, branch_record, qty):
        """Create or update regular PO"""
        vendor = (bom_line.product_id.seller_ids.filtered(lambda s: s.main_vendor)[:1]
                  or bom_line.product_id._select_seller())

        if not vendor or not vendor.partner_id:
            return

        existing_po = self.env['purchase.order'].search([
            ('partner_id', '=', vendor.partner_id.id),
            ('cfe', '=', False),
            ('state', '=', 'draft'),
        ], limit=1)

        if not existing_po:
            existing_po = self.env['purchase.order'].create({
                'partner_id': vendor.partner_id.id,
                'cfe': False,
                'cfe_project_location_id': branch_record.location_id.id,
                'origin': f'Auto Order - {root_bom.display_name}',
            })

        existing_line = existing_po.order_line.filtered(
            lambda l: l.product_id == bom_line.product_id and bom_line.id in l.bom_line_ids.ids
        )

        price = vendor.price or bom_line.product_id.list_price or 0.0

        if existing_line:
            existing_line.product_qty = qty
        else:
            self.env['purchase.order.line'].create({
                'order_id': existing_po.id,
                'product_id': bom_line.product_id.id,
                'product_qty': qty,
                'product_uom': bom_line.product_id.uom_po_id.id,
                'price_unit': price,
                'name': bom_line.product_id.display_name,
                'bom_line_ids': [(4, bom_line.id)],
            })

    def _remove_cfe_po_line(self, bom_line, branch_record):
        """Remove CFE PO line"""
        po_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', bom_line.product_id.id),
            ('bom_line_ids', 'in', [bom_line.id]),
            ('bom_id', '=', branch_record.bom_id.id),
            ('order_id.cfe', '=', True),
            ('order_id.state', '=', 'draft'),
        ])
        po_lines.unlink()

    def _remove_regular_po_line(self, bom_line, branch_record):
        """Remove regular PO line"""
        po_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', bom_line.product_id.id),
            ('bom_line_ids', 'in', [bom_line.id]),
            ('bom_id', '=', branch_record.bom_id.id),
            ('order_id.cfe', '=', False),
            ('order_id.state', '=', 'draft'),
        ])
        po_lines.unlink()