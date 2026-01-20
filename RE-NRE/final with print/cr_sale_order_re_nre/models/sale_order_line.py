from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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

    def action_open_nre_sub_lines(self):
        self.ensure_one()

        # Build One2many commands only for existing lines
        line_commands = [(0, 0, {
            'everest_pn': sub.everest_pn,
            'product_id': sub.product_id.id,
            'billing_percentage': sub.billing_percentage,
            'sub_line_description': sub.sub_line_description,
            'sub_line_code': sub.sub_line_code,
            'required_delivery_date': sub.required_delivery_date,
            'updated_delivery_date': sub.updated_delivery_date,
            'invoice_id': sub.invoice_id.id,  # <--- new
            'invoicing_status': sub.invoicing_status,  # show status
        }) for sub in self.nre_sub_line_ids]

        wizard = self.env['sale.order.line.nre.sub.wizard'].create({
            'sale_line_id': self.id,
            'line_ids': line_commands
        })

        return {
            'name': f'NRE Sub Lines - {self.product_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line.nre.sub.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def _update_delivered_qty_from_sub_lines(self):
        """Update parent line qty_delivered based on sub-lines"""
        self.ensure_one()
        self.qty_delivered = sum(self.re_sub_line_ids.mapped('qty_delivered'))
        print('self.qty_delivered : ',self.qty_delivered)


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
                sub_line_everest_pn = f"{base_everest_pn}.{str(i).zfill(2)}"
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



































