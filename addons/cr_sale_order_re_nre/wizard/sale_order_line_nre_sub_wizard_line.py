# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class NRESubLineWizardLine(models.TransientModel):
    """Wizard Lines for NRE Sub-line"""
    _name = 'sale.order.line.nre.sub.wizard.line'
    _description = 'NRE Sub-line Wizard Line'

    wizard_id = fields.Many2one(
        'sale.order.line.nre.sub.wizard',
        string="Wizard",
        ondelete="cascade"
    )

    everest_pn = fields.Char(
        string="Everest PN",
        compute="_compute_defaults",
        store=False,
        readonly=False
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        compute="_compute_defaults",
        store=False,
        readonly=False
    )
    sub_line_code = fields.Char(
        string="Sub Line Code",
        compute="_compute_defaults",
        store=False,
        readonly=False
    )

    billing_percentage = fields.Float(string="Billing %")
    sub_line_description = fields.Text(string="Sub-line Description")
    required_delivery_date = fields.Date(string="Required Delivery Date",required=True)
    updated_delivery_date = fields.Date(string="Updated Delivery Date")
    selected = fields.Boolean(string="Select")
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        readonly=True,
        domain=[('move_type', '=', 'out_invoice')],
    )
    invoicing_status = fields.Selection([
        ("to_invoice", "To Invoice"),
        ("invoiced", "Invoiced"),
    ], string="Invoicing Status", default="to_invoice")
    billing_amount = fields.Float(
        string="Billing Amount",
        compute='_compute_billing_amount',
        store=False
    )

    @api.depends('billing_percentage')
    def _compute_billing_amount(self):
        """
        Compute billing amount based on the billing percentage
        of the wizard line against its parent sale order line subtotal.
        """
        for line in self:
            if line.wizard_id and line.wizard_id.sale_line_id:
                total_amount = line.wizard_id.sale_line_id.price_subtotal
                line.billing_amount = total_amount * (line.billing_percentage or 0.0) / 100.0

    @api.depends('wizard_id.line_ids')
    def _compute_defaults(self):
        """
        Auto-generate default values (everest_pn, product, sub_line_code)
        for each wizard line based on:
        - Related sale order line details
        - Line sequence within wizard
        - Fallback SO number if everest_pn is missing
        """
        for wizard in self.mapped('wizard_id'):
            if not wizard.sale_line_id:
                continue

            sale_line = wizard.sale_line_id
            order_lines = sale_line.order_id.order_line.sorted('id')
            line_number = list(order_lines).index(sale_line) + 1
            line_number_str = str(line_number).zfill(2)

            base_pn = sale_line.everest_pn or ''
            if not base_pn:
                # fallback if everest_pn not computed yet
                so_number = sale_line.order_id.name
                if so_number.startswith('S'):
                    so_digits = so_number[1:].zfill(5)[-5:]
                else:
                    numeric_part = ''.join(filter(str.isdigit, so_number))
                    so_digits = numeric_part.zfill(5)[-5:]

                qty_formatted = str(int(sale_line.product_uom_qty)).zfill(2)
                row_formatted = line_number_str
                base_pn = f"EVR{so_digits}.{qty_formatted}.{row_formatted}"

            # Enumerate wizard lines so we know row order (1,2,3,...)
            for idx, line in enumerate(wizard.line_ids, start=1):
                suffix = str(idx).zfill(2)
                default_everest_pn = f"{base_pn}.{suffix}"  # Replace last part
                # default_sub_line_code = f"EVR.{line_number_str}.{suffix}"
                default_sub_line_code = False

                if not line.everest_pn:
                    line.everest_pn = default_everest_pn
                if not line.product_id:
                    line.product_id = sale_line.product_id
                if not line.sub_line_code:
                    line.sub_line_code = default_sub_line_code

    @api.onchange('billing_percentage')
    def _onchange_billing_percentage(self):
        """
        Validate billing percentages dynamically.
        Prevents total percentage across wizard lines from exceeding 100%.
        Raises a ValidationError if the limit is crossed.
        """
        if not self.wizard_id:
            return

        sum_other = sum(line.billing_percentage for line in self.wizard_id.line_ids if line.id != self.id)

        if sum_other > 100:
            raise ValidationError(_(
                "Total Billing Percentage cannot exceed 100%. "
                "Current total would be {:.2f}%".format(sum_other)
            ))