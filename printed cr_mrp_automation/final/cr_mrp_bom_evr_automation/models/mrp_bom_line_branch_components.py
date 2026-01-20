# models/mrp_bom_line_branch_components.py
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MrpBomLineBranchComponents(models.Model):
    _inherit = "mrp.bom.line.branch.components"

    def _process_purchase_flow(self):
        """Process purchase flow for this component"""
        self.ensure_one()

        bom_line = self.cr_bom_line_id
        if not bom_line:
            return

        # Check if approvals are TRUE
        if not (bom_line.approval_1 and bom_line.approval_2):
            return

        # Process CFE flow
        self._process_cfe_flow()

        # Process regular purchase flow
        self._process_regular_flow()

    def _process_cfe_flow(self):
        """Process CFE (Customer Furnished Equipment) flow"""
        self.ensure_one()

        bom_line = self.cr_bom_line_id
        cfe_qty = float(bom_line.cfe_quantity or 0)

        if cfe_qty <= 0:
            return

        # Check if CFE is already fully used
        if cfe_qty == self.used:
            return

        root_bom = self.root_bom_id
        customer = root_bom.project_id.partner_id if root_bom.project_id else False

        if not customer:
            return

        # 1. Calculate Transferred CFE
        transferred_cfe = self._calculate_transferred_cfe(customer)
        self.transferred_cfe = transferred_cfe

        if self.transferred_cfe >= cfe_qty:
            # 2. Calculate To Transfer CFE
            self.to_transfer_cfe = 0

            # 3. Calculate Ordered CFE
            self.ordered_cfe = 0

            # 4. Calculate To Order CFE
            self.to_order_cfe = 0

        else:
            # 2. Calculate To Transfer CFE
            to_transfer_cfe = self._calculate_to_transfer_cfe(customer, cfe_qty, transferred_cfe)
            self.to_transfer_cfe = to_transfer_cfe

            total = self.transferred_cfe + self.to_transfer_cfe

            print('total cfe : ',total)
            print('cfe_qty : ', cfe_qty)
            print(total < cfe_qty)

            if total < cfe_qty :
                needed = cfe_qty - total
                # 3. Calculate Ordered CFE
                ordered_cfe = self._calculate_ordered_cfe(customer)
                ordered_cfe = min(needed,ordered_cfe)
                self.ordered_cfe = ordered_cfe

                # 4. Calculate To Order CFE
                to_order_cfe = cfe_qty - transferred_cfe - to_transfer_cfe - ordered_cfe
                self.to_order_cfe = max(0, to_order_cfe)

                # 5. Create/Update CFE Purchase Order
                if to_order_cfe > 0:
                    self._create_or_update_cfe_po(customer, to_order_cfe)
                # else:
                #     self._remove_cfe_po_line()
            else:
                self.ordered_cfe = 0
                self.to_order_cfe = 0



    # def _process_regular_flow(self):
    #     """Process regular (non-CFE) purchase flow"""
    #     self.ensure_one()
    #
    #     bom_line = self.cr_bom_line_id
    #     cfe_qty = float(bom_line.cfe_quantity or 0)
    #     # total_qty = float(bom_line.product_qty or 0)
    #     total_qty = self._get_actual_component_quantity()
    #     x_qty = total_qty - cfe_qty
    #
    #     if x_qty <= 0:
    #         return
    #
    #     # Check if fully used
    #     if x_qty == self.used:
    #         return
    #
    #     # 1. Calculate Transferred
    #     transferred = self._calculate_transferred()
    #     self.transferred = transferred
    #
    #
    #     # 2. Calculate To Transfer
    #     to_transfer = self._calculate_to_transfer(x_qty, transferred)
    #     self.to_transfer = to_transfer
    #
    #     # 3. Calculate Ordered
    #     ordered = self._calculate_ordered()
    #     self.ordered = ordered
    #
    #     # 4. Calculate To Order
    #     to_order = x_qty - transferred - to_transfer - ordered
    #     self.to_order = max(0, to_order)
    #
    #     # 5. Create/Update Purchase Order
    #     if to_order > 0:
    #         self._create_or_update_po(to_order)
    #     else:
    #         self._remove_po_line()

    def _process_regular_flow(self):
        """Process regular (non-CFE) purchase flow"""
        self.ensure_one()

        bom_line = self.cr_bom_line_id
        cfe_qty = float(bom_line.cfe_quantity or 0)
        # total_qty = float(bom_line.product_qty or 0)
        total_qty = self._get_actual_component_quantity()
        x_qty = total_qty - cfe_qty

        if x_qty <= 0:
            return

        # Check if fully used
        if x_qty == self.used:
            return

        # 1. Calculate Transferred
        transferred = self._calculate_transferred()
        self.transferred = transferred

        if self.transferred >= x_qty:
            # 2. Calculate To Transfer CFE
            self.to_transfer = 0

            # 3. Calculate Ordered CFE
            self.ordered = 0

            # 4. Calculate To Order CFE
            self.to_order = 0

        else:
            # 2. Calculate To Transfer
            to_transfer = self._calculate_to_transfer(x_qty, transferred)
            self.to_transfer = to_transfer

            total = self.transferred + self.to_transfer

            print('total : ',total)
            print('x_qty : ', x_qty)
            print(total < x_qty)

            if total < x_qty :
                needed = x_qty - total
                # 3. Calculate Ordered
                ordered = self._calculate_ordered()
                ordered = min(needed,ordered)
                self.ordered = ordered

                # 4. Calculate To Order
                print('x_qty : ',x_qty)
                print('transferred : ', transferred)
                print('to_transfer : ', to_transfer)
                print('ordered : ', ordered)
                to_order = x_qty - transferred - to_transfer - ordered
                self.to_order = max(0, to_order)
                print('self.to_order : ',self.to_order)

                # 5. Create/Update Purchase Order
                if to_order > 0:
                    self._create_or_update_po(to_order)
                # else:
                #     self._remove_po_line()
            else:
                self.ordered = 0
                self.to_order = 0


    # def _get_actual_component_quantity(self):
    #     """
    #     Calculate actual component quantity considering parent BOM hierarchy.
    #     For nested BOMs, multiply quantities up the chain.
    #     """
    #     self.ensure_one()
    #
    #     bom_line = self.cr_bom_line_id
    #     if not bom_line:
    #         return 0.0
    #
    #     # Start with the line's own quantity
    #     total_qty = float(bom_line.product_qty or 0)
    #
    #     # If this is a direct component of root BOM, return as-is
    #     if self.is_direct_component:
    #         return total_qty
    #
    #     # For nested components, traverse up the hierarchy
    #     current_bom = self.bom_id
    #     root_bom = self.root_bom_id
    #
    #     # Find the path from current BOM to root BOM
    #     while current_bom and current_bom.id != root_bom.id:
    #         # Find the BOM line that references this current_bom
    #         parent_line = self.env['mrp.bom.line'].search([
    #             ('child_bom_id', '=', current_bom.id),
    #         ], limit=1)
    #
    #         if not parent_line:
    #             break
    #
    #         # Multiply by parent quantity
    #         total_qty *= float(parent_line.product_qty or 1.0)
    #
    #         # Move up to parent BOM
    #         current_bom = parent_line.bom_id
    #
    #     return total_qty

    def _get_actual_component_quantity(self):
        """
        Calculate actual component quantity considering parent BOM hierarchy.
        For nested BOMs, multiply quantities up the chain.
        """
        self.ensure_one()
        bom_line = self.cr_bom_line_id
        if not bom_line:
            return 0.0

        # Start with the line's own quantity
        total_qty = float(bom_line.product_qty or 0)

        # If this is a direct component of root BOM, return as-is
        if self.is_direct_component:
            return total_qty

        # For nested components, traverse up the hierarchy
        current_bom = self.bom_id
        root_bom = self.root_bom_id

        # Find the path from current BOM to root BOM
        while current_bom and current_bom.id != root_bom.id:
            # Get all BOM lines and check their child_bom_id field value
            all_lines = self.env['mrp.bom.line'].search([
                ('product_tmpl_id', '=', current_bom.product_tmpl_id.id),
            ])

            parent_line = False
            for line in all_lines:
                if line.child_bom_id and line.child_bom_id.id == current_bom.id:
                    parent_line = line
                    break

            if not parent_line:
                break

            # Multiply by parent quantity
            total_qty *= float(parent_line.product_qty or 1.0)

            # Move up to parent BOM
            current_bom = parent_line.bom_id

        return total_qty

    def _calculate_transferred_cfe(self, customer):
        """Calculate transferred CFE quantity"""
        StockQuant = self.env["stock.quant"]

        quants = StockQuant.search([
            ("product_id", "=", self.cr_bom_line_id.product_id.id),
            ("location_id", "=", self.location_id.id),
            ("owner_id", "=", customer.id),
        ])

        return sum(quants.mapped("quantity"))

    # def _calculate_to_transfer_cfe(self, customer, cfe_qty, transferred_cfe):
    #     """Calculate to transfer CFE quantity and create/update internal transfers"""
    #     StockMove = self.env["stock.move"]
    #
    #     # Find pending moves to branch location owned by customer
    #     pending_moves = StockMove.search([
    #         ("product_id", "=", self.cr_bom_line_id.product_id.id),
    #         ("location_src_id.location_category", "=", "free"),
    #         ("location_dest_id", "=", self.location_id.id),
    #         ("state", "not in", ["done", "cancel"]),
    #         ("restrict_partner_id", "=", customer.id),
    #     ])
    #
    #     existing_demand = sum(pending_moves.mapped("product_uom_qty"))
    #
    #     # Calculate needed quantity
    #     needed = cfe_qty - transferred_cfe - existing_demand
    #
    #     # if needed > 0:
    #     #     # Check free stock owned by customer
    #     #     free_stock = self._get_free_stock_owned_by(customer)
    #     #     transfer_qty = min(needed, free_stock)
    #     #
    #     #     if transfer_qty > 0:
    #     #         self._create_internal_transfer(customer, transfer_qty)
    #
    #     if needed > 0:
    #         # Check free stock owned by customer
    #         is_internal_transfer = self.get_internal_transfer(customer,self.cr_bom_line_id.product_id,self.location_id)
    #         free_stock = self._get_free_stock_owned_by(customer)
    #
    #     return existing_demand

    def _calculate_to_transfer_cfe(self, customer, cfe_qty, transferred_cfe):
        """Calculate to transfer CFE quantity and create/update internal transfers"""
        StockMove = self.env["stock.move"]

        # Find pending moves to branch location owned by customer
        pending_moves = StockMove.search([
            ("product_id", "=", self.cr_bom_line_id.product_id.id),
            ("location_dest_id", "=", self.location_id.id),
            ("state", "not in", ["done", "cancel"]),
            ("restrict_partner_id", "=", customer.id),
        ])

        # Filter moves from free locations
        pending_moves = pending_moves.filtered(
            lambda m: self._should_consider_location(m.location_id)
        )
        print('pending_moves : ',pending_moves)
        existing_demand = sum(pending_moves.mapped("product_uom_qty"))
        print('existing_demand : ',existing_demand)
        # Calculate needed quantity
        needed = cfe_qty - transferred_cfe - existing_demand
        print('needed : ',needed)

        if needed > 0:
            # Check if internal transfer exists
            picking_type = self.env["stock.picking.type"].search([
                ("code", "=", "internal"),
            ], limit=1)

            existing_picking = self.env["stock.picking"].search([
                ("picking_type_id", "=", picking_type.id),
                ("owner_id", "=", customer.id),
                ("location_dest_id", "=", self.location_id.id),
                ("state", "not in", ["done", "cancel"]),
            ], limit=1)

            if existing_picking:
                existing_picking = existing_picking.filtered(
                    lambda p: self._should_consider_location(p.location_id)
                )

            if existing_picking:
                print('internal transfer exhist..')
                # Check free stock owned by customer
                free_stock = self._get_free_stock_owned_by(customer)
                free_stock = free_stock - transferred_cfe
                print('free_stock : ',free_stock)

                if free_stock > 0:

                    transfer_qty = min(needed, free_stock)
                    print('transfer_qty : ',transfer_qty)

                    # Find or create move line for this product
                    existing_move = existing_picking.move_ids_without_package.filtered(
                        lambda m: m.product_id == self.cr_bom_line_id.product_id
                    )

                    if existing_move:
                        existing_move.product_uom_qty += transfer_qty
                    else:
                        self.env["stock.move"].create({
                            "name": self.cr_bom_line_id.product_id.display_name,
                            "product_id": self.cr_bom_line_id.product_id.id,
                            "product_uom_qty": transfer_qty,
                            "product_uom": self.cr_bom_line_id.product_id.uom_id.id,
                            "picking_id": existing_picking.id,
                            "location_id": existing_picking.location_id.id,
                            "location_dest_id": self.location_id.id,
                            "restrict_partner_id": customer.id,
                        })

                    existing_demand += transfer_qty
            else:
                print('internal transfer not exhist..')
                # Check free stock owned by customer
                free_stock = self._get_free_stock_owned_by(customer)
                free_stock = free_stock - transferred_cfe
                if free_stock > 0:
                    print('needed : ', needed)
                    print('free_stock : ', free_stock)
                    transfer_qty = min(needed, free_stock)
                    print('transfer_qty : ', transfer_qty)
                    print('customer : ', customer)
                    self._create_internal_transfer(customer, transfer_qty)
                    existing_demand += transfer_qty

        return existing_demand

    def _get_free_stock_owned_by(self, partner):
        """Get free stock quantity owned by specific partner"""
        StockQuant = self.env["stock.quant"]

        quants = StockQuant.search([
            ("product_id", "=", self.cr_bom_line_id.product_id.id),
            ("owner_id", "=", partner.id),
            ("quantity", ">", 0),
        ])

        total = 0.0
        for quant in quants:
            if self._should_consider_location(quant.location_id):
                total += quant.quantity

        return total

    def _should_consider_location(self, location):
        """
        Check if a location should be considered by checking itself and then its parent chain.
        Returns True if the location itself OR any of its ancestors is marked as free.
        Stops checking as soon as a free location is found.
        """
        if not location:
            return False

        cur = location
        while cur:
            is_free = getattr(cur, 'location_category', False) == 'free'

            if is_free:
                return True

            cur = cur.location_id

        return False

    def _calculate_ordered_cfe(self, customer):
        """Calculate ordered CFE quantity from confirmed POs"""
        POLine = self.env["purchase.order.line"]

        po_lines = POLine.search([
            ("component_branch_id", "=", self.id),
            ("order_id.partner_id", "=", customer.id),
            ("order_id.state", "in", ["purchase", "done"]),
            # ("order_id.cfe", "=", True),
        ])
        print('po_lines : ',po_lines)
        return sum(po_lines.mapped("product_qty"))

    def _calculate_transferred(self):
        """Calculate transferred quantity (non-CFE)"""
        StockQuant = self.env["stock.quant"]

        quants = StockQuant.search([
            ("product_id", "=", self.cr_bom_line_id.product_id.id),
            ("location_id", "=", self.location_id.id),
            ("owner_id", "=", False),
        ])

        return sum(quants.mapped("quantity"))

    # def _calculate_to_transfer(self, x_qty, transferred):
    #     """Calculate to transfer quantity and create/update internal transfers"""
    #     StockMove = self.env["stock.move"]
    #
    #     # Find pending moves to branch location without owner
    #     pending_moves = StockMove.search([
    #         ("product_id", "=", self.cr_bom_line_id.product_id.id),
    #         ("location_dest_id", "=", self.location_id.id),
    #         ("state", "not in", ["done", "cancel"]),
    #         ("restrict_partner_id", "=", False),
    #     ])
    #
    #     existing_demand = sum(pending_moves.mapped("product_uom_qty"))
    #
    #     # Calculate needed quantity
    #     needed = x_qty - transferred - existing_demand
    #
    #     if needed > 0:
    #         # Check free stock
    #         free_stock = self.free_to_use
    #         transfer_qty = min(needed, free_stock)
    #
    #         if transfer_qty > 0:
    #             self._create_internal_transfer(False, transfer_qty)
    #
    #     return existing_demand

    def _calculate_to_transfer(self, x_qty, transferred):
        """Calculate to transfer quantity and create/update internal transfers"""
        print('')
        print('')
        print('==============================')
        StockMove = self.env["stock.move"]

        # Find pending moves to branch location without owner
        pending_moves = StockMove.search([
            ("product_id", "=", self.cr_bom_line_id.product_id.id),
            ("location_dest_id", "=", self.location_id.id),
            ("state", "not in", ["done", "cancel"]),
            ("restrict_partner_id", "=", False),
        ])
        print('pending_moves : ',pending_moves)
        # Filter moves from free locations
        pending_moves = pending_moves.filtered(
            lambda m: self._should_consider_location(m.location_id)
        )
        print('pending_moves : ',pending_moves)

        existing_demand = sum(pending_moves.mapped("product_uom_qty"))

        # Calculate needed quantity
        print('x_qty : ',x_qty)
        print('transferred : ', transferred)
        print('existing_demand : ', existing_demand)
        needed = x_qty - transferred - existing_demand
        print('needed : ',needed)
        if needed > 0:
            # Check if internal transfer exists
            picking_type = self.env["stock.picking.type"].search([
                ("code", "=", "internal"),
            ], limit=1)

            existing_picking = self.env["stock.picking"].search([
                ("picking_type_id", "=", picking_type.id),
                ("owner_id", "=", False),
                ("location_dest_id", "=", self.location_id.id),
                ("state", "not in", ["done", "cancel"]),
            ], limit=1)
            print('existing_picking : ',existing_picking)

            if existing_picking:
                existing_picking = existing_picking.filtered(
                    lambda p: self._should_consider_location(p.location_id)
                )

            if existing_picking:
                # Check free stock
                free_stock = self._get_free_stock_without_owner()
                print('1 normal free_stock : ',free_stock)
                free_stock = free_stock - transferred
                print('free_stock : ',free_stock)

                if free_stock > 0:
                    transfer_qty = min(needed, free_stock)
                    print(' transfer_qty : ',transfer_qty)
                    # Find or create move line for this product
                    existing_move = existing_picking.move_ids_without_package.filtered(
                        lambda m: m.product_id == self.cr_bom_line_id.product_id
                    )
                    print('existing_move : ',existing_move)
                    if existing_move:
                        print('existing_move.product_uom_qty : ',existing_move.product_uom_qty)
                        existing_move.product_uom_qty += transfer_qty
                        print('existing_move.product_uom_qty : ', existing_move.product_uom_qty)
                    else:
                        print('new move create...')
                        self.env["stock.move"].create({
                            "name": self.cr_bom_line_id.product_id.display_name,
                            "product_id": self.cr_bom_line_id.product_id.id,
                            "product_uom_qty": transfer_qty,
                            "product_uom": self.cr_bom_line_id.product_id.uom_id.id,
                            "picking_id": existing_picking.id,
                            "location_id": existing_picking.location_id.id,
                            "location_dest_id": self.location_id.id,
                            "restrict_partner_id": False,
                        })

                    existing_demand += transfer_qty
            else:
                # Check free stock
                free_stock = self._get_free_stock_without_owner()
                free_stock = free_stock - transferred
                print('in else..')
                print('free_stock : ',free_stock)
                if free_stock > 0:
                    transfer_qty = min(needed, free_stock)
                    print('transfer_qty : ',transfer_qty)
                    new_tr = self._create_internal_transfer(False, transfer_qty)
                    print('new internal transfer..',new_tr)
                    existing_demand += transfer_qty

        return existing_demand

    def _get_free_stock_without_owner(self):
        """Get free stock quantity without owner"""
        StockQuant = self.env["stock.quant"]

        quants = StockQuant.search([
            ("product_id", "=", self.cr_bom_line_id.product_id.id),
            ("owner_id", "=", False),
            ("quantity", ">", 0),
        ])

        total = 0.0
        for quant in quants:
            if self._should_consider_location(quant.location_id):
                total += quant.quantity

        return total

    def _calculate_ordered(self):
        """Calculate ordered quantity from confirmed POs (non-CFE)"""
        POLine = self.env["purchase.order.line"]

        vendor = (self.cr_bom_line_id.product_id.seller_ids.filtered(lambda s: s.main_vendor)[:1]
                  or self.cr_bom_line_id.product_id._select_seller())

        po_lines = POLine.search([
            ("component_branch_id", "=", self.id),
            ("order_id.partner_id", "=", vendor.id),
            ("order_id.state", "in", ["purchase", "done"]),
            # ("order_id.cfe", "=", False),
        ])
        print('po_lines : ',po_lines)

        if len(po_lines) == 1:
            print('order : ',po_lines.order_id)
        return sum(po_lines.mapped("product_qty"))

    def _get_free_stock_owned_by(self, partner):
        """Get free stock quantity owned by specific partner"""
        StockQuant = self.env["stock.quant"]
        StockLocation = self.env["stock.location"]

        # Find all free locations
        free_locations = StockLocation.search([
            ("location_category", "=", "free")
        ])

        quants = StockQuant.search([
            ("product_id", "=", self.cr_bom_line_id.product_id.id),
            ("location_id", "in", free_locations.ids),
            ("owner_id", "=", partner.id),
        ])

        return sum(quants.mapped("quantity"))

    def _create_internal_transfer(self, owner, quantity):
        """Create internal transfer to branch location"""
        StockPicking = self.env["stock.picking"]
        StockLocation = self.env["stock.location"]

        # Find source location (free location with stock)
        free_locations = StockLocation.search([
            ("location_category", "=", "free")
        ])

        picking_type = self.env["stock.picking.type"].search([
            ("code", "=", "internal"),
            ("company_id", "=", self.root_bom_id.company_id.id),
        ], limit=1)

        if not picking_type or not free_locations:
            return

        vendor = (self.cr_bom_line_id.product_id.seller_ids.filtered(lambda s: s.main_vendor)[:1]
                  or self.cr_bom_line_id.product_id._select_seller())

        picking_vals = {
            "picking_type_id": picking_type.id,
            "location_dest_id": self.location_id.id,
            "origin": f"EVR Flow - {self.root_bom_id.display_name}",
            "partner_id":vendor.id,
            "owner_id": owner.id if owner else False,
            "move_ids": [(0, 0, {
                "name": self.cr_bom_line_id.product_id.display_name,
                "product_id": self.cr_bom_line_id.product_id.id,
                "product_uom_qty": quantity,
                "product_uom": self.cr_bom_line_id.product_id.uom_id.id,
                "location_dest_id": self.location_id.id,
                "restrict_partner_id": owner.id if owner else False,
            })],
        }
        print('picking_vals : ',picking_vals)
        StockPicking.create(picking_vals)

    def _create_or_update_cfe_po(self, customer, quantity):
        """Create or update CFE purchase order"""
        print('yes in create po..')
        POLine = self.env["purchase.order.line"]
        PO = self.env["purchase.order"]

        # Find existing draft CFE PO line for this component
        existing_line = POLine.search([
            ("component_branch_id", "=", self.id),
            ("order_id.partner_id", "=", customer.id),
            ("order_id.state", "=", "draft"),
            ("bom_id", "=", self.root_bom_id.id),
            # ("order_id.cfe", "=", True),
        ], limit=1)
        print('existing_line : ',existing_line)

        if existing_line:
            print('yes existing_line...')
            print('before product_qty : ', existing_line.product_qty)
            if existing_line.product_qty != quantity:
                existing_line.product_qty = quantity
            print('after product_qty : ', existing_line.product_qty)
            self.cr_bom_line_id.customer_po_line_id = POLine.id
            print('self.cr_bom_line_id : ',self.cr_bom_line_id)
            print('self.cr_bom_line_id.customer_po_line_id : ', self.cr_bom_line_id.customer_po_line_id)
            print('POLine.id : ',POLine.id)
        else:
            # Find or create CFE PO
            po = PO.search([
                ("partner_id", "=", customer.id),
                ("state", "=", "draft"),
                # ("cfe", "=", True),
                ("bom_id", "=", self.root_bom_id.id),
            ], limit=1)

            if not po:
                po = PO.create({
                    "partner_id": customer.id,
                    "bom_id": self.root_bom_id.id,
                    "origin": f"EVR Flow - {self.root_bom_id.display_name}",
                    "cfe_project_location_id": self.root_bom_id.cfe_project_location_id.id,
                    "state":'draft',
                })
                print('new po : ',po)

            POLine.create({
                "order_id": po.id,
                "product_id": self.cr_bom_line_id.product_id.id,
                "product_qty": quantity,
                "product_uom": self.cr_bom_line_id.product_id.uom_po_id.id,
                "price_unit": 0.0,
                "date_planned": fields.Datetime.now(),
                "component_branch_id": self.id,
                "bom_line_ids": [(6, 0, [self.cr_bom_line_id.id])],
                "bom_id":self.root_bom_id.id,
            })

            find_cpo_line = self.env["purchase.order.line"].search(
                [('product_id', '=', self.cr_bom_line_id.product_id.id), ('order_id', '=', po.id),('component_branch_id','=',self.id)])
            self.cr_bom_line_id.customer_po_line_id = find_cpo_line.id
            print('new po line : ', find_cpo_line)


    def _create_or_update_po(self, quantity):
        """Create or update regular purchase order"""
        print('')
        print('in regular po..')
        POLine = self.env["purchase.order.line"]
        PO = self.env["purchase.order"]

        bom_line = self.cr_bom_line_id
        vendor = (bom_line.product_id.seller_ids.filtered(lambda s: s.main_vendor)[:1]
                  or bom_line.product_id._select_seller())

        if not vendor or not vendor.partner_id:
            return

        # Find existing draft PO line for this component
        existing_line = POLine.search([
            ("component_branch_id", "=", self.id),
            ("order_id.partner_id", "=", vendor.partner_id.id),
            ("order_id.state", "=", "draft"),
            ("bom_id", "=", self.root_bom_id.id),
            # ("order_id.cfe", "=", False),
        ], limit=1)
        print('existing_line : ',existing_line)

        if existing_line:
            # existing_line.product_qty = quantity
            if existing_line.product_qty != quantity:
                existing_line.product_qty = quantity

            self.cr_bom_line_id.po_line_id = POLine.id
        else:
            # Find or create PO
            po = PO.search([
                ("partner_id", "=", vendor.partner_id.id),
                ("state", "=", "draft"),
                # ("cfe", "=", False),
                ("bom_id", "=", self.root_bom_id.id),
            ], limit=1)

            if not po:
                po = PO.create({
                    "partner_id": vendor.partner_id.id,
                    "bom_id": self.root_bom_id.id,
                    "origin": f"EVR Flow - {self.root_bom_id.display_name}",
                    "cfe_project_location_id": self.root_bom_id.cfe_project_location_id.id,
                    "state": 'draft',
                })

            price = vendor.price or bom_line.product_id.list_price

            POLine.create({
                "order_id": po.id,
                "product_id": bom_line.product_id.id,
                "product_qty": quantity,
                "product_uom": bom_line.product_id.uom_po_id.id,
                "price_unit": price,
                "date_planned": fields.Datetime.now(),
                "component_branch_id": self.id,
                "bom_line_ids": [(6, 0, [bom_line.id])],
                "bom_id":self.root_bom_id.id,
            })
            find_vpo_line = self.env["purchase.order.line"].search(
                [('product_id', '=', self.cr_bom_line_id.product_id.id), ('order_id', '=', po.id),
                 ('component_branch_id', '=', self.id)])
            self.cr_bom_line_id.customer_po_line_id = find_vpo_line.id
            print('new po line : ', find_vpo_line)

    def _remove_cfe_po_line(self):
        """Remove CFE PO line if to_order_cfe is 0"""
        POLine = self.env["purchase.order.line"]

        lines = POLine.search([
            ("component_branch_id", "=", self.id),
            ("order_id.state", "=", "draft"),
            ("order_id.cfe", "=", True),
        ])

        for line in lines:
            po = line.order_id
            line.unlink()

            # Remove PO if no lines left
            if not po.order_line:
                po.unlink()

    def _remove_po_line(self):
        """Remove PO line if to_order is 0"""
        POLine = self.env["purchase.order.line"]

        lines = POLine.search([
            ("component_branch_id", "=", self.id),
            ("order_id.state", "=", "draft"),
            ("order_id.cfe", "=", False),
        ])

        for line in lines:
            po = line.order_id
            line.unlink()

            # Remove PO if no lines left
            if not po.order_line:
                po.unlink()

