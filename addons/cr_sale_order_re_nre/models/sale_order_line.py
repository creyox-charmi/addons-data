# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from odoo import api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
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
    remaining_invoiced_amount = fields.Monetary(
        string="Remaining Invoiced Amount",
        compute="_compute_remaining_invoiced_amount",
        store=True,
        currency_field="currency_id",
        help="Amount still to be invoiced for this line, "
             "based on ordered qty minus invoiced qty."
    )

    re_nre_domain = fields.Char(
        compute="_compute_re_nre_domain",
        store=False,
        readonly=True,
    )

    @api.onchange('product_id', 'product_uom_qty', 're_nre')
    def _onchange_re_nre_logic(self):
        for line in self:
            if not line.product_id:
                line.re_nre = False
                continue

            # 🧠 Auto-assign RE/NRE based on product type
            if not line.re_nre:  # Only auto-assign if not manually selected yet
                if line.product_id.type == 'service':
                    line.re_nre = 'nre'
                elif line.product_id.type == 'consu':
                    line.re_nre = 're'

            # 🧩 Case 1 — Service product cannot be RE
            if line.product_id.type == 'service' and line.re_nre == 're':
                raise ValidationError("Service-based products cannot be marked as RE.")

            # 🧩 Case 2 — Non-service cannot be NRE
            if line.product_id.type != 'service' and line.re_nre == 'nre':
                raise ValidationError("Only service-based products can be marked as NRE.")

            # 🧩 Case 3 — Service + NRE + qty > 1
            if line.product_id.type == 'service' and line.re_nre == 'nre' and line.product_uom_qty != 1:
                raise ValidationError("For NRE (service) lines, quantity must be exactly 1.")

            # 🧩 Case 4 — Product changed from service → non-service while still NRE
            if line.re_nre == 'nre' and line.product_id.type != 'service':
                raise ValidationError("NRE can only be used for service-based products.")

            # ✅ Auto-adjust invoice policy
            if line.product_id and line.re_nre:
                if line.re_nre == 're' and line.product_id.invoice_policy != 'delivery':
                    line.product_id.invoice_policy = 'delivery'
                elif line.re_nre == 'nre' and line.product_id.invoice_policy != 'order':
                    line.product_id.invoice_policy = 'order'

    # ---------------------------
    #  CONSTRAINT: Backend safety
    # ---------------------------
    @api.constrains('product_id', 'product_uom_qty', 're_nre')
    def _check_re_nre_constraints(self):
        for line in self:

            if not line.product_id:
                continue

            # 🧩 Case 1 — Service + RE → not allowed
            if line.product_id.type == 'service' and line.re_nre == 're':
                raise ValidationError("Service-based products cannot be marked as RE.")

            # 🧩 Case 2 — Non-service + NRE → not allowed
            if line.product_id.type != 'service' and line.re_nre == 'nre':
                raise ValidationError("Only service-based products can be marked as NRE.")

            # 🧩 Case 3 & 4 — Service + NRE + qty > 1 → not allowed
            if line.product_id.type == 'service' and line.re_nre == 'nre' and line.product_uom_qty != 1:
                raise ValidationError("For NRE (service) lines, quantity must be exactly 1.")

            # 🧩 Case 5 — Product changed (NRE on non-service) → not allowed
            if line.re_nre == 'nre' and line.product_id.type != 'service':
                raise ValidationError("NRE can only be used for service-based products.")

            # ✅ NEW: Invoice Policy Constraint
            if line.product_id and line.re_nre:
                if line.re_nre == 're':
                    if line.product_id.invoice_policy != 'delivery':
                        raise ValidationError(
                            f"Product '{line.product_id.name}' must have Invoice Policy set to "
                            "'Delivered quantities' when RE is selected."
                        )
                elif line.re_nre == 'nre':
                    if line.product_id.invoice_policy != 'order':
                        raise ValidationError(
                            f"Product '{line.product_id.name}' must have Invoice Policy set to "
                            "'Ordered quantities' when NRE is selected."
                        )

    @api.depends(
        'product_uom_qty', 'qty_invoiced', 'price_unit',
        'discount', 'currency_id',
        'nre_sub_line_ids.billing_percentage',
        'nre_sub_line_ids.billing_amount',
        'nre_sub_line_ids.invoiced_amount',
        're_nre'
    )
    def _compute_remaining_invoiced_amount(self):
        """
        Compute remaining invoice amount (without tax).
        - For NRE lines: based on sub-line billing % or fixed billing amount.
        - For RE/other lines: standard qty × price logic.
        """
        for line in self:
            remaining_total =  0

            if line.re_nre == 'nre' and line.nre_sub_line_ids:
                # --- NRE case: compute based on invoiced percentage ---
                for sub in line.nre_sub_line_ids:
                    if sub.invoiced_amount > 0:
                        print('sub.billing_percentage : ', sub.billing_percentage)

                total_percentage = sum(
                    sub.billing_percentage
                    for sub in line.nre_sub_line_ids
                    if sub.invoiced_amount > 0  # only count invoiced subs
                )
                remaining = line.product_uom_qty * (1 - (total_percentage / 100.0))
                line.remaining_qty_to_deliver = max(remaining, 0.0)
                remaining_total = line.remaining_qty_to_deliver * line.price_unit
            else:
                # --- RE / normal lines ---
                remaining_qty = max(line.product_uom_qty - line.qty_invoiced, 0.0)
                if remaining_qty > 0:
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    remaining_total = price * remaining_qty

            line.remaining_invoiced_amount = remaining_total

    @api.depends('nre_sub_line_ids.invoiced_amount', 'price_subtotal')
    def _compute_nre_invoiced_amount(self):
        """Compute invoiced and remaining amounts for NRE sub-lines."""
        for line in self:
            invoiced = sum(line.nre_sub_line_ids.mapped('invoiced_amount'))
            line.nre_invoiced_amount = invoiced
            line.nre_remaining_amount = line.price_subtotal - invoiced

    @api.depends('order_id.order_line')
    def _compute_line_number(self):
        """Compute sequential line numbers within a sale order."""
        for order in self.mapped('order_id'):
            lines = order.order_line.sorted(lambda l: (l.sequence, l.id or 0))
            for index, line in enumerate(lines, 1):
                line.line_number = index

    @api.depends('order_id.name', 'product_uom_qty', 'line_number', 'order_id.state')
    def _compute_everest_pn(self):
        """Generate Everest PN code in format PREFIX + SO number + row."""
        for line in self:
            if line.order_id and line.line_number:
                if line.order_id.state == 'sale' and line.order_id.name:
                    # Confirmed order: EVR prefix with SO number
                    so_number = line.order_id.name
                    if so_number.startswith('S'):
                        so_digits = so_number[1:].zfill(5)[-5:]
                    else:
                        numeric_part = ''.join(filter(str.isdigit, so_number))
                        so_digits = numeric_part.zfill(5)[-5:]

                    row_formatted = str(line.line_number).zfill(2)
                    line.everest_pn = f"EVR{so_digits}.{row_formatted}"
                else:
                    # Quotation stage: GEN with simple sequence
                    line.everest_pn = f"GEN{str(line.line_number).zfill(3)}"
            else:
                line.everest_pn = False

    @api.depends('product_uom_qty', 'qty_delivered',
                 'nre_sub_line_ids.billing_percentage', 'nre_sub_line_ids.invoiced_amount')
    def _compute_remaining_qty(self):
        """Compute remaining quantity to deliver for RE and NRE lines."""
        for line in self:
            if line.re_nre == "nre" and line.nre_sub_line_ids:
                # --- NRE case: compute based on invoiced percentage ---
                for sub in line.nre_sub_line_ids:
                    if sub.invoiced_amount > 0:
                        print('sub.billing_percentage : ',sub.billing_percentage)


                total_percentage = sum(
                    sub.billing_percentage
                    for sub in line.nre_sub_line_ids
                    if sub.invoiced_amount > 0  # only count invoiced subs
                )
                remaining = line.product_uom_qty * (1 - (total_percentage / 100.0))
                line.remaining_qty_to_deliver = max(remaining, 0.0)
            else:
                # --- RE or normal line: qty based ---
                line.remaining_qty_to_deliver = line.product_uom_qty - line.qty_delivered

    @api.model_create_multi
    def create(self, vals_list):
        """Recompute line numbers and update product default_code (Everest PN)
        when adding lines — even after order confirmation.
        """
        lines = super().create(vals_list)

        for line in lines:
            # --- Recompute line numbering ---
            if line.order_id:
                line.order_id.order_line._compute_line_number()

            # --- Handle Everest PN update for confirmed/done orders ---
            order = line.order_id
            product = line.product_id
            everest_pn = line.everest_pn

            # Run only if order is confirmed/done
            if order.state in ['sale', 'done']:
                if not product or not everest_pn:
                    _logger.warning(
                        f"Skipping Everest PN update for line {line.id}: "
                        f"missing product or everest_pn."
                    )
                    continue

                template = product.product_tmpl_id
                variant_count = len(template.product_variant_ids)

                if variant_count == 1:
                    # Update template (single variant)
                    _logger.info(
                        f"[Post-Confirm Add] Single Variant: Updating Template '{template.name}' "
                        f"(ID: {template.id}) default_code -> {everest_pn}"
                    )
                    template.default_code = everest_pn
                else:
                    # Update specific variant (multi variant)
                    _logger.info(
                        f"[Post-Confirm Add] Multi Variant: Updating Variant '{product.display_name}' "
                        f"(ID: {product.id}) default_code -> {everest_pn}"
                    )
                    product.default_code = everest_pn

        return lines


    def write(self, vals):
            """SuperCall write to recompute line numbers if sequence is updated."""
            result = super().write(vals)
            if 'sequence' in vals:
                orders = self.mapped('order_id')
                for order in orders:
                    order.order_line._compute_line_number()
            return result

    def unlink(self):
        """SuperCall unlink to recompute line numbers after record deletion."""
        orders = self.mapped('order_id')
        result = super().unlink()
        for order in orders:
            if order.exists():
                order.order_line._compute_line_number()
        return result

    @api.depends('nre_sub_line_ids.invoiced_amount')
    def _compute_invoiced_amounts(self):
        """Compute total invoiced and remaining amounts for NRE lines."""
        for line in self:
            if line.re_nre == 'nre' and line.nre_sub_line_ids:
                line.total_invoiced_amount = sum(line.nre_sub_line_ids.mapped('invoiced_amount'))
                line.remaining_amount_to_invoice = line.price_subtotal - line.total_invoiced_amount
            else:
                line.total_invoiced_amount = 0.0
                line.remaining_amount_to_invoice = line.price_subtotal

    def action_open_re_sub_lines(self):
        """Open a popup window showing RE sub-lines of the sale order line."""
        self.ensure_one()
        if self.re_nre == 're':
            self._generate_re_sub_lines()
        return {
            'name': f'RE Sub Lines - {self.product_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line.re.sub',
            'view_mode': 'list',
            'domain': [('sale_line_id', '=', self.id)],
            'context': {'default_sale_line_id': self.id,
                        'hide_delivery_dates': self.order_id.state != 'sale',  # Add this
                        },
            'target': 'new',
        }

    def action_open_nre_sub_lines(self):
        """Open a popup wizard to manage NRE sub-lines of the sale order line."""
        self.ensure_one()
        line_commands = [(0, 0, {
            'everest_pn': sub.everest_pn,
            'product_id': sub.product_id.id,
            'billing_percentage': sub.billing_percentage,
            'sub_line_description': sub.sub_line_description,
            # 'sub_line_code': sub.sub_line_code,
            'required_delivery_date': sub.required_delivery_date,
            'updated_delivery_date': sub.updated_delivery_date,
            'invoice_id': sub.invoice_id.id,
            'invoicing_status': sub.invoicing_status,
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
            'context': {'hide_delivery_dates': self.order_id.state != 'sale',  # Add this
                        },

        }

    def _update_delivered_qty_from_sub_lines(self):
        """Update parent line delivered quantity from RE sub-lines."""
        self.ensure_one()
        self.qty_delivered = sum(self.re_sub_line_ids.mapped('qty_delivered'))


    def action_sync_re_sub_lines(self,delivery_name=None):
        """Sync sub-lines with delivered quantities and update delivery info."""
        self.ensure_one()

        if self.re_nre != 're':
            return

        if not self.re_sub_line_ids:
            self._generate_re_sub_lines()
        already_delivered = len(self.re_sub_line_ids.filtered(lambda l: l.qty_delivered > 0))
        delivered_qty = int(self.qty_delivered or 0)
        new_deliveries = delivered_qty - already_delivered
        if new_deliveries <= 0:
            return
        pending_sub_lines = (
            self.re_sub_line_ids
            .filtered(lambda l: l.qty_delivered == 0)
            .sorted('id')[:new_deliveries]
        )
        for sub_line in pending_sub_lines:
            sub_line.write({
                "qty_delivered": 1.0,
                "remaining_qty_to_deliver": 0.0,
                "delivery_note_number": delivery_name,
            })


    def write(self, vals):
        result = super().write(vals)
        if "product_uom_qty" in vals or "re_nre" in vals:
            for line in self:
                if line.re_nre == "re":
                    line._generate_re_sub_lines()
        return result

    def _generate_re_sub_lines(self):
        """Generate or update RE sub-lines based on quantity changes."""
        self.ensure_one()
        if self.re_nre != "re":
            return

        delivered_qty = int(self.qty_delivered or 0)
        target_qty = int(self.product_uom_qty or 0)

        existing_sub_lines = self.re_sub_line_ids.sorted('id')
        current_qty = len(existing_sub_lines)

        base_everest_pn = self.everest_pn
        order_lines = self.order_id.order_line.sorted('id')
        line_number = list(order_lines).index(self) + 1
        line_number_str = str(line_number).zfill(2)

        # 🔹 Case A: Increase quantity → add new sub-lines
        if target_qty > current_qty:
            new_lines = []
            for i in range(current_qty + 1, target_qty + 1):
                base_everest_pn = self._get_evr_base_code()

                sub_line_everest_pn = f"{base_everest_pn}.{str(i).zfill(2)}"

                vals = {
                    "sale_line_id": self.id,
                    "everest_pn": sub_line_everest_pn,
                    # "sub_line_code": sub_line_code,
                    "quantity": 1.0,
                    "qty_delivered": 1.0 if i <= delivered_qty else 0.0,
                    "remaining_qty_to_deliver": 0.0 if i <= delivered_qty else 1.0,
                }
                new_lines.append(vals)
            self.env["sale.order.line.re.sub"].create(new_lines)

        # 🔹 Case B: Decrease quantity → remove extra sub-lines
        elif target_qty < current_qty:
            extra_sub_lines = existing_sub_lines[target_qty:]
            if any(sl.qty_delivered > 0 for sl in extra_sub_lines):
                raise ValidationError(
                    f"You cannot reduce quantix`ty below {current_qty} "
                    f"because some sub-lines are already delivered."
                )
            extra_sub_lines.unlink()

        # 🔹 Case C: Update codes & delivery status for all sub-lines
        for idx, sub_line in enumerate(self.re_sub_line_ids.sorted('id'), start=1):
            is_delivered = idx <= delivered_qty
            base_everest_pn = self._get_evr_base_code()

            sub_line_everest_pn = f"{base_everest_pn}.{str(idx).zfill(2)}"
            vals = {
                "everest_pn": sub_line_everest_pn,
                "qty_delivered": 1.0 if is_delivered else 0.0,
                "remaining_qty_to_deliver": 0.0 if is_delivered else 1.0,
            }
            sub_line.write(vals)

    def _get_evr_base_code(self):
        """Always generate EVR base code using SO number and line number"""
        self.ensure_one()

        order = self.order_id
        if not order or not order.name:
            return False

        so_number = order.name

        if so_number.startswith('S'):
            so_digits = so_number[1:].zfill(5)[-5:]
        else:
            numeric_part = ''.join(filter(str.isdigit, so_number))
            so_digits = numeric_part.zfill(5)[-5:]

        row_formatted = str(self.line_number).zfill(2)

        return f"EVR{so_digits}.{row_formatted}"


    def _get_invoiceable_lines(self, final=False):
        """
        Override to exclude NRE lines from standard invoicing flow.
        NRE lines should only be invoiced via the NRE wizard.
        """
        invoiceable_lines = super()._get_invoiceable_lines(final=final)
        # Filter out NRE lines
        return invoiceable_lines.filtered(lambda l: l.re_nre != 'nre')

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        """
        Override to exclude NRE lines from standard invoicing.
        NRE lines are invoiced only through the NRE wizard.
        """
        invoiceable_lines = super()._get_invoiceable_lines(final=final)
        # Exclude NRE lines from standard invoicing
        return invoiceable_lines.filtered(lambda line: line.re_nre != 'nre')


