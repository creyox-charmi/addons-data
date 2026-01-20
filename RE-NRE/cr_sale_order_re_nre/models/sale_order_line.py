# # models/sale_order_line.py
# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
#
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     # 1. Line Number
#     line_number = fields.Integer(
#         string='Line N',
#         compute='_compute_line_number',
#         store=True,
#         help='Sequential line number starting from 1'
#     )
#
#     # 2. Everest PN
#     everest_pn = fields.Char(
#         string='Everest PN',
#         compute='_compute_everest_pn',
#         store=True,
#         help='Generated part number: EVR + SO Number + Quantity + Row'
#     )
#
#     # 3. Customer PN
#     customer_pn = fields.Char(
#         string='Customer PN',
#         help='Customer Part Number - to be filled manually'
#     )
#
#     # 6. Remaining quantity to deliver
#     remaining_qty_to_deliver = fields.Float(
#         string='Remaining Qty to Deliver',
#         compute='_compute_remaining_qty',
#         store=True,
#         help='Quantity remaining to be delivered'
#     )
#
#     # 8. RE & NRE Field
#     re_nre = fields.Selection([
#         ('re', 'RE'),
#         ('nre', 'NRE')
#     ], string='RE & NRE', help='Select RE or NRE')
#
#     # 12. Required Delivery Date
#     required_delivery_date = fields.Date(
#         string='Required Delivery Date',
#         help='Expected delivery date'
#     )
#
#     # 13. Updated Delivery Date
#     updated_delivery_date = fields.Date(
#         string='Updated Delivery Date',
#         help='Actual delivery date after or before required date'
#     )
#
#     @api.depends('order_id.order_line')
#     def _compute_line_number(self):
#         """Compute sequential line numbers for each sale order"""
#         for order in self.mapped('order_id'):
#             lines = order.order_line.sorted(lambda l: (l.id, l.sequence))
#             for index, line in enumerate(lines, 1):
#                 line.line_number = index
#
#     @api.depends('order_id.name', 'product_uom_qty', 'line_number')
#     def _compute_everest_pn(self):
#         """Generate Everest PN: EVR + 5-digit SO number + 2-digit qty + 2-digit row"""
#         for line in self:
#             if line.order_id and line.order_id.name and line.line_number:
#                 # Extract 5 digits from sale order number
#                 so_number = line.order_id.name
#                 # Remove 'S' prefix and get 5 digits
#                 if so_number.startswith('S'):
#                     so_digits = so_number[1:].zfill(5)[-5:]
#                 else:
#                     # Extract numeric part and pad to 5 digits
#                     numeric_part = ''.join(filter(str.isdigit, so_number))
#                     so_digits = numeric_part.zfill(5)[-5:]
#
#                 # Format quantity to 2 digits
#                 qty_formatted = str(int(line.product_uom_qty)).zfill(2)
#
#                 # Format row number to 2 digits
#                 row_formatted = str(line.line_number).zfill(2)
#
#                 # Generate Everest PN
#                 line.everest_pn = f"EVR{so_digits}.{qty_formatted}.{row_formatted}"
#             else:
#                 line.everest_pn = False
#
#     @api.depends('product_uom_qty', 'qty_delivered')
#     def _compute_remaining_qty(self):
#         """Calculate remaining quantity to deliver"""
#         for line in self:
#             line.remaining_qty_to_deliver = line.product_uom_qty - line.qty_delivered
#
#     @api.model
#     def create(self, vals):
#         """Override create to ensure line numbers are computed"""
#         line = super().create(vals)
#         # Trigger recomputation of line numbers for all lines in the order
#         if line.order_id:
#             line.order_id.order_line._compute_line_number()
#         return line
#
#     def write(self, vals):
#         """Override write to recompute line numbers if sequence changes"""
#         result = super().write(vals)
#         if 'sequence' in vals:
#             # Recompute line numbers for affected orders
#             orders = self.mapped('order_id')
#             for order in orders:
#                 order.order_line._compute_line_number()
#         return result
#
#     def unlink(self):
#         """Override unlink to recompute line numbers after deletion"""
#         orders = self.mapped('order_id')
#         result = super().unlink()
#         # Recompute line numbers for affected orders
#         for order in orders:
#             if order.exists():
#                 order.order_line._compute_line_number()
#         return result


# models/sale_order_line.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        readonly=False,
        search='_search_product_template_id',
        context={'display_default_code': False},
        # previously related='product_id.product_tmpl_id'
        # not anymore since the field must be considered editable for product configurator logic
        # without modifying the related product_id when updated.
        domain=[('sale_ok', '=', True)])

    # 1. Line Number
    line_number = fields.Integer(
        string='Line N',
        compute='_compute_line_number',
        store=True,
        help='Sequential line number starting from 1'
    )

    # 2. Everest PN
    everest_pn = fields.Char(
        string='Everest PN',
        compute='_compute_everest_pn',
        store=True,
        help='Generated part number: EVR + SO Number + Quantity + Row'
    )

    # 3. Customer PN
    customer_pn = fields.Char(
        string='Customer PN',
        help='Customer Part Number - to be filled manually'
    )

    # 6. Remaining quantity to deliver
    remaining_qty_to_deliver = fields.Float(
        string='Remaining Qty to Deliver',
        compute='_compute_remaining_qty',
        store=True,
        help='Quantity remaining to be delivered'
    )

    # 8. RE & NRE Field
    re_nre = fields.Selection([
        ('re', 'RE'),
        ('nre', 'NRE')
    ], string='RE & NRE', help='Select RE or NRE')

    # 12. Required Delivery Date
    required_delivery_date = fields.Date(
        string='Required Delivery Date',
        help='Expected delivery date'
    )

    # 13. Updated Delivery Date
    updated_delivery_date = fields.Date(
        string='Updated Delivery Date',
        help='Actual delivery date after or before required date',
    )

    re_sub_line_ids = fields.One2many(
        'sale.order.line.re.sub',
        'sale_line_id',
        string='RE Sub Lines'
    )

    nre_sub_line_ids = fields.One2many(
        'sale.order.line.nre.sub',
        'sale_line_id',
        string='NRE Sub Lines'
    )

    nre_invoiced_amount = fields.Float(
        string='Invoiced Amount',
        compute='_compute_nre_invoiced_amount',
        store=True
    )
    nre_remaining_amount = fields.Float(
        string='Remaining Amount',
        compute='_compute_nre_invoiced_amount',
        store=True
    )

    @api.depends('nre_sub_line_ids.invoiced_amount', 'price_subtotal')
    def _compute_nre_invoiced_amount(self):
        for line in self:
            invoiced = sum(line.nre_sub_line_ids.mapped('invoiced_amount'))
            line.nre_invoiced_amount = invoiced
            line.nre_remaining_amount = line.price_subtotal - invoiced


    @api.depends('order_id.order_line')
    def _compute_line_number(self):
        """Compute sequential line numbers for each sale order"""
        for order in self.mapped('order_id'):
            # Use sequence first, then fallback on real ID (0 if NewId)
            lines = order.order_line.sorted(lambda l: (l.sequence, l.id or 0))
            for index, line in enumerate(lines, 1):
                line.line_number = index

    # @api.depends('order_id.order_line')
    # def _compute_line_number(self):
    #     """Compute sequential line numbers for each sale order"""
    #     for order in self.mapped('order_id'):
    #         lines = order.order_line.sorted(lambda l: (l.id, l.sequence))
    #         for index, line in enumerate(lines, 1):
    #             line.line_number = index

    # @api.depends('qty_delivered', 'product_uom_qty')
    # def _compute_updated_delivery_date(self):
    #     """Set updated delivery date when all quantity is delivered"""
    #     for line in self:
    #         if line.product_uom_qty > 0 and line.qty_delivered >= line.product_uom_qty:
    #             # Only set if not already set manually
    #             if not line.updated_delivery_date:
    #                 line.updated_delivery_date = date.today()
    #                 print(f"[DEBUG] Updated delivery date set for SO Line {line.id}")
    #         else:
    #             line.updated_delivery_date = False

    @api.depends('order_id.name', 'product_uom_qty', 'line_number')
    def _compute_everest_pn(self):
        """Generate Everest PN: EVR + 5-digit SO number + 2-digit qty + 2-digit row"""
        for line in self:
            if line.order_id and line.order_id.name and line.line_number:
                # Extract 5 digits from sale order number
                so_number = line.order_id.name
                # Remove 'S' prefix and get 5 digits
                if so_number.startswith('S'):
                    so_digits = so_number[1:].zfill(5)[-5:]
                else:
                    # Extract numeric part and pad to 5 digits
                    numeric_part = ''.join(filter(str.isdigit, so_number))
                    so_digits = numeric_part.zfill(5)[-5:]

                # Format quantity to 2 digits
                qty_formatted = str(int(line.product_uom_qty)).zfill(2)

                # Format row number to 2 digits
                row_formatted = str(line.line_number).zfill(2)

                # Generate Everest PN
                line.everest_pn = f"EVR{so_digits}.{qty_formatted}.{row_formatted}"
            else:
                line.everest_pn = False

    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_remaining_qty(self):
        """Calculate remaining quantity to deliver"""
        for line in self:
            line.remaining_qty_to_deliver = line.product_uom_qty - line.qty_delivered

    @api.model
    def create(self, vals):
        """Override create to ensure line numbers are computed"""
        line = super().create(vals)
        # Trigger recomputation of line numbers for all lines in the order
        if line.order_id:
            line.order_id.order_line._compute_line_number()
        return line

    def write(self, vals):
        """Override write to recompute line numbers if sequence changes"""
        result = super().write(vals)
        if 'sequence' in vals:
            # Recompute line numbers for affected orders
            orders = self.mapped('order_id')
            for order in orders:
                order.order_line._compute_line_number()
        return result

    def unlink(self):
        """Override unlink to recompute line numbers after deletion"""
        orders = self.mapped('order_id')
        result = super().unlink()
        # Recompute line numbers for affected orders
        for order in orders:
            if order.exists():
                order.order_line._compute_line_number()
        return result

    @api.depends('nre_sub_line_ids.invoiced_amount')
    def _compute_invoiced_amounts(self):
        """Calculate total invoiced and remaining amounts for NRE lines"""
        for line in self:
            if line.re_nre == 'nre' and line.nre_sub_line_ids:
                line.total_invoiced_amount = sum(line.nre_sub_line_ids.mapped('invoiced_amount'))
                line.remaining_amount_to_invoice = line.price_subtotal - line.total_invoiced_amount
            else:
                line.total_invoiced_amount = 0.0
                line.remaining_amount_to_invoice = line.price_subtotal

    def action_open_re_sub_lines(self):
        """Open RE sub-lines popup"""
        self.ensure_one()
        if self.re_nre == 're':
            self._generate_re_sub_lines()

        return {
            'name': f'RE Sub Lines - {self.product_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line.re.sub',
            'view_mode': 'list',
            'domain': [('sale_line_id', '=', self.id)],
            'context': {'default_sale_line_id': self.id},
            'target': 'new',
        }

    # def action_open_nre_sub_lines(self):
    #     """Open NRE sub-lines popup"""
    #     self.ensure_one()
    #     return {
    #         'name': f'NRE Sub Lines - {self.product_id.name}',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'sale.order.line.nre.sub',
    #         'view_mode': 'list',
    #         'domain': [('sale_line_id', '=', self.id)],
    #         'context': {'default_sale_line_id': self.id},
    #         'target': 'new',
    #     }

    def action_open_nre_sub_lines(self):
        """Open NRE sub-lines popup"""
        self.ensure_one()

        # Get SO line number (position in order)
        order_lines = self.order_id.order_line.sorted('id')
        line_number = list(order_lines).index(self) + 1
        line_number_str = str(line_number).zfill(2)

        # Prepare defaults
        next_index = len(self.nre_sub_line_ids) + 1
        base_pn = self.everest_pn or ''
        default_everest_pn = f"{base_pn}.{str(next_index).zfill(2)}"
        default_sub_line_code = f"EVR.{line_number_str}.{str(next_index).zfill(2)}"  # << same as RE style

        return {
            'name': f'NRE Sub Lines - {self.product_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line.nre.sub',
            'view_mode': 'list',
            'domain': [('sale_line_id', '=', self.id)],
            'context': {
                'default_sale_line_id': self.id,
                'default_product_id': self.product_id.id,
                'default_everest_pn': default_everest_pn,
                'default_sub_line_code': default_sub_line_code,  # << generated same as RE
            },
            'target': 'new',
        }

    def _update_delivered_qty_from_sub_lines(self):
        """Update parent line qty_delivered based on sub-lines"""
        self.ensure_one()
        self.qty_delivered = sum(self.re_sub_line_ids.mapped('qty_delivered'))
        print('self.qty_delivered : ',self.qty_delivered)

    # def _generate_re_sub_lines(self):
    #     """Auto-generate RE sub-lines based on quantity"""
    #     self.ensure_one()
    #     print('>>>>>self.re_sub_line_ids ',self.re_sub_line_ids)
    #     if not self.re_sub_line_ids and self.product_uom_qty > 0:
    #         sub_lines = []
    #         base_everest_pn = self.everest_pn.rsplit('.', 1)[0]  # Remove last part
    #
    #         for i in range(1, int(self.product_uom_qty) + 1):
    #             sub_line_everest_pn = f"{base_everest_pn}.{str(i).zfill(3)}"
    #             sub_lines.append({
    #                 'sale_line_id': self.id,
    #                 'everest_pn': sub_line_everest_pn,
    #                 'quantity': 1.0,
    #                 # 'sub_line_code': f"SUB-{str(i).zfill(3)}",
    #                 'required_delivery_date': self.required_delivery_date,
    #                 'updated_delivery_date': self.updated_delivery_date,
    #             })
    #
    #         self.env['sale.order.line.re.sub'].create(sub_lines)

    # def action_sync_re_sub_lines(self, delivery_date=None):
    #     """Sync RE sub-lines with delivered qty"""
    #     self.ensure_one()
    #     delivered_qty = int(self.qty_delivered or 0)
    #
    #     for index, sub in enumerate(self.re_sub_line_ids.sorted('id'), start=1):
    #         if index <= delivered_qty:
    #             sub.write({
    #                 'qty_delivered': 1.0,
    #                 'remaining_qty_to_deliver': 0.0,
    #                 'updated_delivery_date': delivery_date or date.today(),
    #                 'state': 'delivered',
    #             })
    #         else:
    #             sub.write({
    #                 'qty_delivered': 0.0,
    #                 'remaining_qty_to_deliver': 1.0,
    #                 'state': 'pending',
    #             })

    # def action_sync_re_sub_lines(self, delivery_date=None, delivery_name=None):
    #     """Sync RE sub-lines after delivery"""
    #     self.ensure_one()
    #     if self.re_nre != 're':
    #         return
    #
    #     delivered_qty = int(self.qty_delivered or 0)
    #     sub_lines = self.re_sub_line_ids.sorted('id')
    #
    #     print(f"[DEBUG] Syncing {delivered_qty} delivered qty for {len(sub_lines)} RE sub-lines")
    #
    #     # Count how many sub-lines were already delivered before this sync
    #     already_delivered = sum(1 for sl in sub_lines if sl.qty_delivered > 0)
    #
    #     print(f"[DEBUG] Already delivered before this sync: {already_delivered}")
    #
    #     for i, sub_line in enumerate(sub_lines, start=1):
    #         print("111111")
    #         if i <= delivered_qty:
    #             # This sub-line should be marked delivered
    #             if sub_line.qty_delivered == 0:  # ✅ deliver only new ones
    #                 sub_line.qty_delivered = 1.0
    #                 sub_line.remaining_qty_to_deliver = 0.0
    #                 sub_line.updated_delivery_date = delivery_date or date.today()
    #                 if delivery_name:
    #                     sub_line.delivery_note_number = delivery_name
    #                 print(f"[DEBUG] NEWLY delivered Sub-line {sub_line.id}: "
    #                       f"delivery_note_number={sub_line.delivery_note_number}")
    #             else:
    #                 print(f"[DEBUG] Sub-line {sub_line.id} already delivered, skipping update")
    #         else:
    #             # Not yet delivered → keep pending
    #             sub_line.qty_delivered = 0.0
    #             sub_line.remaining_qty_to_deliver = 1.0

    def action_sync_re_sub_lines(self, delivery_date=None, delivery_name=None):
        """Sync RE sub-lines after delivery, using delivery_date + delivery_name"""
        self.ensure_one()
        if self.re_nre != 're':
            return

        # always ensure sub-lines exist
        if not self.re_sub_line_ids:
            self._generate_re_sub_lines()

        # how many qtys are already marked delivered
        already_delivered = len(self.re_sub_line_ids.filtered(lambda l: l.qty_delivered > 0))

        # total delivered on sale order line (from stock moves)
        delivered_qty = int(self.qty_delivered or 0)

        # how many new ones to mark in this sync
        new_deliveries = delivered_qty - already_delivered
        if new_deliveries <= 0:
            return

        print(
            f"[SYNC] SO Line {self.id}: Delivered {delivered_qty}, Already {already_delivered}, "
            f"Marking {new_deliveries} with {delivery_name}"
        )

        # assign delivery note only to the *next* set of pending sub-lines
        pending_sub_lines = (
            self.re_sub_line_ids
            .filtered(lambda l: l.qty_delivered == 0)
            .sorted('id')[:new_deliveries]
        )

        for sub_line in pending_sub_lines:
            sub_line.write({
                "qty_delivered": 1.0,
                "remaining_qty_to_deliver": 0.0,
                "updated_delivery_date": delivery_date or fields.Date.today(),
                "delivery_note_number": delivery_name,
            })
            print(
                f"[SYNC][UPDATE] Sub-line {sub_line.id} → Delivered via {delivery_name}"
            )

    # def _generate_re_sub_lines(self):
    #     """Auto-generate or sync RE sub-lines based on quantity and delivered qty"""
    #     self.ensure_one()
    #
    #     delivered_qty = int(self.qty_delivered or 0)
    #     base_everest_pn = self.everest_pn.rsplit('.', 1)[0] if self.everest_pn else ""
    #
    #     print(f"[DEBUG] Generating RE Sub-lines for SO Line {self.id} ({self.product_id.display_name})")
    #     print(f"[DEBUG] Total Ordered Qty: {self.product_uom_qty}, Already Delivered Qty: {delivered_qty}")
    #
    #     if not self.re_sub_line_ids and self.product_uom_qty > 0:
    #         # CASE 1: No sub-lines → create them
    #         sub_lines = []
    #         for i in range(1, int(self.product_uom_qty) + 1):
    #             sub_line_everest_pn = f"{base_everest_pn}.{str(i).zfill(3)}"
    #             is_delivered = i <= delivered_qty
    #
    #             vals = {
    #                 'sale_line_id': self.id,
    #                 'everest_pn': sub_line_everest_pn,
    #                 'quantity': 1.0,
    #                 'qty_delivered': 1.0 if is_delivered else 0.0,
    #                 'remaining_qty_to_deliver': 0.0 if is_delivered else 1.0,
    #                 'required_delivery_date': self.required_delivery_date,
    #                 'updated_delivery_date': date.today() if is_delivered else False,
    #             }
    #             print(f"[DEBUG][CREATE] Sub-line {i} → {vals}")
    #             sub_lines.append(vals)
    #
    #         self.env['sale.order.line.re.sub'].create(sub_lines)
    #
    #     else:
    #         # CASE 2: Sub-lines already exist → update them
    #         for idx, sub_line in enumerate(self.re_sub_line_ids.sorted('id'), start=1):
    #             is_delivered = idx <= delivered_qty
    #             vals = {
    #                 'qty_delivered': 1.0 if is_delivered else 0.0,
    #                 'remaining_qty_to_deliver': 0.0 if is_delivered else 1.0,
    #                 'updated_delivery_date': date.today() if is_delivered else False,
    #             }
    #             print(f"[DEBUG][UPDATE] Sub-line {idx} ({sub_line.everest_pn}) → {vals}")
    #             sub_line.write(vals)

    def _generate_re_sub_lines(self):
        """Auto-generate or sync RE sub-lines based on quantity and delivered qty"""
        self.ensure_one()

        delivered_qty = int(self.qty_delivered or 0)
        base_everest_pn = self.everest_pn.rsplit('.', 1)[0] if self.everest_pn else ""

        # Get SO line number (position in order)
        order_lines = self.order_id.order_line.sorted('id')
        line_number = list(order_lines).index(self) + 1
        line_number_str = str(line_number).zfill(2)

        print(f"[DEBUG] Generating RE Sub-lines for SO Line {self.id} ({self.product_id.display_name})")
        print(
            f"[DEBUG] SO Line Number: {line_number}, Total Ordered Qty: {self.product_uom_qty}, Already Delivered Qty: {delivered_qty}")

        if not self.re_sub_line_ids and self.product_uom_qty > 0:
            # CASE 1: No sub-lines → create them
            sub_lines = []
            for i in range(1, int(self.product_uom_qty) + 1):
                sub_line_everest_pn = f"{base_everest_pn}.{str(i).zfill(3)}"
                sub_line_code = f"EVR.{line_number_str}.{str(i).zfill(2)}"  # << new logic

                is_delivered = i <= delivered_qty
                vals = {
                    'sale_line_id': self.id,
                    'everest_pn': sub_line_everest_pn,
                    'sub_line_code': sub_line_code,  # << new field
                    'quantity': 1.0,
                    'qty_delivered': 1.0 if is_delivered else 0.0,
                    'remaining_qty_to_deliver': 0.0 if is_delivered else 1.0,
                    'required_delivery_date': self.required_delivery_date,
                    'updated_delivery_date': date.today() if is_delivered else False,
                }
                print(f"[DEBUG][CREATE] Sub-line {i} → {vals}")
                sub_lines.append(vals)

            self.env['sale.order.line.re.sub'].create(sub_lines)

        else:
            # CASE 2: Sub-lines already exist → update them
            for idx, sub_line in enumerate(self.re_sub_line_ids.sorted('id'), start=1):
                sub_line_code = f"EVR.{line_number_str}.{str(idx).zfill(2)}"  # regenerate code

                is_delivered = idx <= delivered_qty
                vals = {
                    'sub_line_code': sub_line_code,  # << keep codes consistent
                    'qty_delivered': 1.0 if is_delivered else 0.0,
                    'remaining_qty_to_deliver': 0.0 if is_delivered else 1.0,
                    'updated_delivery_date': date.today() if is_delivered else False,
                }
                print(f"[DEBUG][UPDATE] Sub-line {idx} ({sub_line.everest_pn}) → {vals}")
                sub_line.write(vals)


class SaleOrderLineRESub(models.Model):
    """RE Sub-lines for recurring deliveries"""
    _name = 'sale.order.line.re.sub'
    _description = 'Sale Order Line RE Sub Lines'
    _order = 'sale_line_id, sequence, id'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Sequence', default=10)
    everest_pn = fields.Char(string='Everest PN', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    remaining_qty_to_deliver = fields.Float(
        string='Remaining Qty to Deliver',
        compute='_compute_remaining_qty',
        store=True
    )
    qty_delivered = fields.Float(string='Delivered Qty', default=0.0)
    delivery_note_number = fields.Char(string='Delivery Note Number')
    required_delivery_date = fields.Date(string='Required Delivery Date')
    updated_delivery_date = fields.Date(string='Updated Delivery Date')
    sub_line_code = fields.Char(string='Sub Line Code')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('invoiced', 'Invoiced')
    ], string='Status', default='pending')

    @api.depends('quantity', 'qty_delivered')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty_to_deliver = line.quantity - line.qty_delivered

    def action_mark_delivered(self):
        """Mark sub-line as delivered"""
        self.ensure_one()
        self.qty_delivered = self.quantity
        self.state = 'delivered'
        # Update parent line delivered quantity
        self.sale_line_id._update_delivered_qty_from_sub_lines()

    def action_create_delivery(self):
        """Create delivery for selected sub-lines"""
        # Implementation for delivery creation
        pass


class SaleOrderLineNRESub(models.Model):
    """NRE Sub-lines for milestone billing"""
    _name = 'sale.order.line.nre.sub'
    _description = 'Sale Order Line NRE Sub Lines'
    _order = 'sale_line_id, sequence, id'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Sequence', default=10)
    everest_pn = fields.Char(
        string='Everest PN',
        required=True,
        compute='_compute_nre_fields',
        store=True,
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        compute='_compute_nre_fields',
        store=True,
        readonly=True
    )
    billing_percentage = fields.Float(string='Billing %', required=True)
    sub_line_description = fields.Text(string='Sub-line Description')
    sub_line_code = fields.Char(string='Sub Line Code')
    required_delivery_date = fields.Date(string='Required Delivery Date')
    updated_delivery_date = fields.Date(string='Updated Delivery Date')

    # Computed billing amounts
    billing_amount = fields.Float(
        string='Billing Amount',
        compute='_compute_billing_amount',
        store=True
    )
    invoiced_amount = fields.Float(string='Invoiced Amount', default=0.0)

    invoicing_status = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready to Invoice'),
        ('invoiced', 'Invoiced')
    ], string='Invoicing Status', default='pending')

    @api.depends('sale_line_id', 'sale_line_id.nre_sub_line_ids', 'sale_line_id.product_id')
    def _compute_nre_fields(self):
        """Compute Everest PN and Product ID"""
        for sub in self:
            if not sub.sale_line_id:
                sub.everest_pn = False
                sub.product_id = False
                continue

            # Set product_id from parent SO line
            sub.product_id = sub.sale_line_id.product_id

            # Compute Everest PN
            siblings = sub.sale_line_id.nre_sub_line_ids.sorted('id')

            # Safe way to get index
            try:
                index = siblings.ids.index(sub.id) + 1 if sub.id in siblings.ids else len(siblings) + 1
            except ValueError:
                index = len(siblings) + 1

            base_pn = sub.sale_line_id.everest_pn or ''
            sub.everest_pn = f"{base_pn}.{str(index).zfill(2)}"

    @api.depends('billing_percentage', 'sale_line_id.price_subtotal')
    def _compute_billing_amount(self):
        for line in self:
            if line.sale_line_id:
                line.billing_amount = (line.billing_percentage / 100.0) * line.sale_line_id.price_subtotal
            else:
                line.billing_amount = 0.0

    def action_create_invoice(self):
        """Create invoice for this milestone"""
        self.ensure_one()
        if self.invoicing_status != 'pending':
            raise ValidationError("This milestone has already been invoiced!")

        # Create invoice line
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.sale_line_id.order_id.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': f"{self.sale_line_id.name} - {self.sub_line_description or 'Milestone'}",
                'quantity': 1,
                'price_unit': self.billing_amount,
                'sale_line_ids': [(4, self.sale_line_id.id)],
            })],
        }

        invoice = self.env['account.move'].create(invoice_vals)

        # Update status and invoiced amount
        self.invoiced_amount = self.billing_amount
        self.invoicing_status = 'invoiced'

        # Update parent line amounts
        self.sale_line_id._compute_invoiced_amounts()

        return {
            'name': 'Invoice Created',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_mark_ready_to_invoice(self):
        """Mark milestone as ready to invoice"""
        self.invoicing_status = 'ready'

    def action_create_invoice(self):
        """Create invoice(s) for selected milestones"""
        invoices = self.env['account.move']
        for sub in self:
            if sub.invoicing_status != 'pending':
                continue

            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': sub.sale_line_id.order_id.partner_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f"{sub.sale_line_id.name} - {sub.sub_line_description or 'Milestone'}",
                    'quantity': 1,
                    'price_unit': sub.billing_amount,
                    'sale_line_ids': [(4, sub.sale_line_id.id)],
                })],
            }
            invoice = self.env['account.move'].create(invoice_vals)
            invoices |= invoice

            sub.invoiced_amount = sub.billing_amount
            sub.invoicing_status = 'invoiced'
            sub.sale_line_id._compute_invoiced_amounts()

        if len(invoices) == 1:
            return {
                'name': 'Invoice',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': invoices.id,
                'view_mode': 'form',
                'target': 'current',
            }
        elif invoices:
            return {
                'name': 'Invoices',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'domain': [('id', 'in', invoices.ids)],
                'view_mode': 'tree,form',
                'target': 'current',
            }
        return True


# # Extension to handle delivery updates
# class SaleOrderLineExtended(models.Model):
#     _inherit = 'sale.order.line'
#
#     def _update_delivered_qty_from_sub_lines(self):
#         """Update main line delivered quantity from RE sub-lines"""
#         if self.re_nre == 're' and self.re_sub_line_ids:
#             total_delivered = sum(self.re_sub_line_ids.mapped('qty_delivered'))
#             self.qty_delivered = total_delivered


# models/sub_line_wizard.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RESubLineWizard(models.TransientModel):
    """Wizard for managing RE sub-lines with delivery tracking"""
    _name = 'sale.order.line.re.wizard'
    _description = 'RE Sub-line Management Wizard'

    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', required=True)
    re_sub_line_ids = fields.One2many(
        'sale.order.line.re.sub.wizard.line',
        'wizard_id',
        string='RE Sub Lines'
    )
    total_qty = fields.Float(related='sale_line_id.product_uom_qty', string='Total Quantity')
    delivered_qty = fields.Float(related='sale_line_id.qty_delivered', string='Delivered Quantity')
    remaining_qty = fields.Float(related='sale_line_id.remaining_qty_to_deliver', string='Remaining Quantity')

    @api.model
    def default_get(self, fields_list):
        print("calllllllllllllllllllllllllllll")
        res = super().default_get(fields_list)
        if self.env.context.get('active_id'):
            sale_line = self.env['sale.order.line'].browse(self.env.context['active_id'])
            res['sale_line_id'] = sale_line.id

            # Load existing sub-lines or create new ones
            if sale_line.re_sub_line_ids:
                wizard_lines = []
                for sub_line in sale_line.re_sub_line_ids:
                    wizard_lines.append({
                        'sub_line_id': sub_line.id,
                        'everest_pn': sub_line.everest_pn,
                        'quantity': sub_line.quantity,
                        'qty_delivered': sub_line.qty_delivered,
                        'delivery_note_number': sub_line.delivery_note_number,
                        'required_delivery_date': sub_line.required_delivery_date,
                        'updated_delivery_date': sub_line.updated_delivery_date,
                        'selected_for_delivery': False,
                    })
                res['re_sub_line_ids'] = [(0, 0, line) for line in wizard_lines]
        return res

    # without print
    # @api.model
    # def default_get(self, fields_list):
    #     """Pre-populate wizard lines based on sale order line quantities"""
    #     res = super().default_get(fields_list)
    #
    #     sale_line_id = self.env.context.get('active_id')
    #     if not sale_line_id:
    #         return res
    #
    #     sale_line = self.env['sale.order.line'].browse(sale_line_id)
    #
    #     wizard_lines = []
    #     delivered_qty = int(sale_line.qty_delivered)
    #     total_qty = int(sale_line.product_uom_qty)
    #
    #     for i in range(1, total_qty + 1):
    #         wizard_lines.append((0, 0, {
    #             'everest_pn': sale_line.everest_pn,
    #             'quantity': 1,  # each row = 1 qty
    #             'qty_delivered': 0 if i <= delivered_qty else 1,  # already delivered → lock
    #             'delivery_note_number': '',
    #             'required_delivery_date': sale_line.required_delivery_date,
    #             'updated_delivery_date': sale_line.updated_delivery_date,
    #         }))
    #
    #     res['sale_line_id'] = sale_line.id
    #     res['re_sub_line_ids'] = wizard_lines
    #     return res

    # @api.model
    # def default_get(self, fields_list):
    #     """Pre-populate wizard lines based on sale order line quantities"""
    #     res = super().default_get(fields_list)
    #
    #     sale_line_id = self.env.context.get('active_id')
    #     if not sale_line_id:
    #         return res
    #
    #     sale_line = self.env['sale.order.line'].browse(sale_line_id)
    #
    #     wizard_lines = []
    #     delivered_qty = int(sale_line.qty_delivered)
    #     total_qty = int(sale_line.product_uom_qty)
    #
    #     print(">>> Opening RE Wizard for Sale Order Line ID: %s", sale_line.id)
    #     print(">>> Product: %s | Total Qty: %s | Delivered Qty: %s | Remaining: %s",
    #                  sale_line.product_id.display_name,
    #                  total_qty,
    #                  delivered_qty,
    #                  total_qty - delivered_qty)
    #
    #     for i in range(1, total_qty + 1):
    #         delivered_flag = (i <= delivered_qty)
    #         wizard_lines.append((0, 0, {
    #             'everest_pn': sale_line.everest_pn,
    #             'quantity': 1,  # each row = 1 qty
    #             'qty_delivered': 0 if delivered_flag else 1,
    #             'delivery_note_number': '',
    #             'required_delivery_date': sale_line.required_delivery_date,
    #             'updated_delivery_date': sale_line.updated_delivery_date,
    #         }))
    #         print(">>> Row %s | Delivered Already: %s | Qty Delivered Pre-set: %s",
    #                      i, delivered_flag, 0 if delivered_flag else 1)
    #
    #     res['sale_line_id'] = sale_line.id
    #     res['re_sub_line_ids'] = wizard_lines
    #
    #     print(">>> Wizard Lines Prepared: %s", len(wizard_lines))
    #     return res

    def action_confirm_deliveries(self):
        """Process selected deliveries and update quantities"""
        selected_lines = self.re_sub_line_ids.filtered('selected_for_delivery')
        if not selected_lines:
            raise ValidationError("Please select at least one line for delivery.")

        for wizard_line in selected_lines:
            if wizard_line.sub_line_id:
                wizard_line.sub_line_id.write({
                    'qty_delivered': wizard_line.quantity,
                    'state': 'delivered',
                    'delivery_note_number': wizard_line.delivery_note_number,
                    'updated_delivery_date': wizard_line.updated_delivery_date,
                })

        # Update main line delivered quantity
        self.sale_line_id._update_delivered_qty_from_sub_lines()

        return {'type': 'ir.actions.act_window_close'}

    def action_generate_sub_lines(self):
        """Generate sub-lines if they don't exist"""
        self.sale_line_id._generate_re_sub_lines()
        return self.default_get([])


class RESubLineWizardLine(models.TransientModel):
    """Wizard lines for RE sub-line management"""
    _name = 'sale.order.line.re.sub.wizard.line'
    _description = 'RE Sub-line Wizard Line'

    wizard_id = fields.Many2one('sale.order.line.re.wizard', required=True)
    sub_line_id = fields.Many2one('sale.order.line.re.sub', string='Sub Line')
    selected_for_delivery = fields.Boolean(string='Select for Delivery')
    everest_pn = fields.Char(string='Everest PN', readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    qty_delivered = fields.Float(string='Delivered Qty')
    delivery_note_number = fields.Char(string='Delivery Note')
    required_delivery_date = fields.Date(string='Required Date')
    updated_delivery_date = fields.Date(string='Delivery Date')


# class NRESubLineWizard(models.TransientModel):
#     """Wizard for managing NRE sub-lines with milestone billing"""
#     _name = 'sale.order.line.nre.sub.wizard.line'
#     _description = 'NRE Sub-line Wizard Line'


# from datetime import date
#
# class StockPicking(models.Model):
#     _inherit = "stock.picking"
#
#     def button_validate(self):
#         res = super().button_validate()
#
#         for move in self.move_ids_without_package:
#             sale_line = move.sale_line_id
#             if sale_line and sale_line.re_nre == 're':
#                 # After delivery, sync RE sub-lines
#                 sale_line.action_sync_re_sub_lines(delivery_date=date.today())
#
#         return res


from datetime import date
from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    # def button_validate(self):
    #     res = super().button_validate()
    #
    #     for move in self.move_ids_without_package:
    #         so_line = move.sale_line_id
    #         if not so_line:
    #             continue
    #
    #         # 1️⃣ Update main line updated_delivery_date if fully delivered
    #         if so_line.product_uom_qty > 0 and so_line.qty_delivered >= so_line.product_uom_qty:
    #             if not so_line.updated_delivery_date:
    #                 so_line.write({'updated_delivery_date': date.today()})
    #                 print(f"[DEBUG] Updated delivery date set for SO Line {so_line.id}")
    #
    #         # 2️⃣ Sync RE sub-lines if line is RE
    #         if so_line.re_nre == 're':
    #             print(f"[DEBUG] Syncing RE sub-lines for SO Line {so_line.id}")
    #             so_line.action_sync_re_sub_lines(delivery_date=date.today())
    #
    #     return res

    def button_validate(self):
        res = super().button_validate()

        for move in self.move_ids_without_package:
            so_line = move.sale_line_id
            if not so_line:
                continue

            # # 1️⃣ Update main line updated_delivery_date if fully delivered
            # if so_line.product_uom_qty > 0 and so_line.qty_delivered >= so_line.product_uom_qty:
            #     if not so_line.updated_delivery_date:
            #         so_line.write({'updated_delivery_date': date.today()})
            #         print(f"[DEBUG] Updated delivery date set for SO Line {so_line.id}")

            # 2️⃣ Sync RE sub-lines if line is RE
            if so_line.re_nre == 're':
                print(f"[DEBUG] Syncing RE sub-lines for SO Line {so_line.id}")
                # Pass the delivery/picking name here
                print(f"move {move}")
                print(f"move.picking_id {move.picking_id}")
                print(f"move.picking_id.name {move.picking_id.name}")
                so_line.action_sync_re_sub_lines(delivery_name=move.picking_id.name if move.picking_id else None)

        return res


from odoo import models, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('name', 'default_code')
    def _compute_display_name(self):
        print('yessssssssss')
        for template in self:
            # Show only product name, ignore default_code
            template.display_name = template.name or ''

from odoo import models, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends('name', 'product_tmpl_id', 'product_template_attribute_value_ids')
    @api.depends_context('seller_id', 'company_id', 'partner_id')
    def _compute_display_name(self):
        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')

        self.check_access("read")

        product_template_ids = self.sudo().product_tmpl_id.ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search_fetch(
                [('product_tmpl_id', 'in', product_template_ids), ('partner_id', 'in', partner_ids)],
                ['product_tmpl_id', 'product_id', 'company_id', 'product_name'],
            )
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)

        for product in self.sudo():
            variant = product.product_template_attribute_value_ids._get_combination_name()
            # Only use name + variant, no default_code
            name = variant and "%s (%s)" % (product.name, variant) or product.name

            sellers = self.env['product.supplierinfo'].sudo().browse(self.env.context.get('seller_id')) or []
            if not sellers and partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
                if company_id:
                    sellers = [x for x in sellers if x.company_id.id in [company_id, False]]

            if sellers:
                temp = []
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    temp.append(seller_variant or name)

                product.display_name = ", ".join(set(temp))
            else:
                product.display_name = name















