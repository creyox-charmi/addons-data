from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

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
    required_delivery_date = fields.Date(string="Required Delivery Date")
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
        for line in self:
            if line.wizard_id and line.wizard_id.sale_line_id:
                total_amount = line.wizard_id.sale_line_id.price_subtotal
                line.billing_amount = total_amount * (line.billing_percentage or 0.0) / 100.0
                # print for debug
                _logger.info(">>> Computed billing_amount %s for wizard line %s", line.billing_amount, line.id)

    # @api.depends('wizard_id.line_ids')
    # def _compute_defaults(self):
    #     for wizard in self.mapped('wizard_id'):
    #         if not wizard.sale_line_id:
    #             continue
    #
    #         sale_line = wizard.sale_line_id
    #         order_lines = sale_line.order_id.order_line.sorted('id')
    #         line_number = list(order_lines).index(sale_line) + 1
    #         line_number_str = str(line_number).zfill(2)
    #
    #         base_pn = sale_line.everest_pn or ''
    #
    #         # Enumerate wizard lines so we know row order (1,2,3,...)
    #         for idx, line in enumerate(wizard.line_ids, start=1):
    #             suffix = str(idx).zfill(2)
    #             default_everest_pn = f"{base_pn}.{suffix}"
    #             default_sub_line_code = f"EVR.{line_number_str}.{suffix}"
    #
    #             if not line.everest_pn:
    #                 line.everest_pn = default_everest_pn
    #             if not line.product_id:
    #                 line.product_id = sale_line.product_id
    #             if not line.sub_line_code:
    #                 line.sub_line_code = default_sub_line_code

    @api.depends('wizard_id.line_ids')
    def _compute_defaults(self):
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
                default_everest_pn = f"{base_pn[:-3]}.{suffix}"  # Replace last part
                default_sub_line_code = f"EVR.{line_number_str}.{suffix}"

                if not line.everest_pn:
                    line.everest_pn = default_everest_pn
                if not line.product_id:
                    line.product_id = sale_line.product_id
                if not line.sub_line_code:
                    line.sub_line_code = default_sub_line_code

    # @api.depends('wizard_id', 'wizard_id.line_ids')
    # def _compute_defaults(self):
    #     for line in self:
    #         wizard = line.wizard_id
    #         if wizard:
    #             row_index = len(wizard.line_ids.filtered(lambda l: l.id != line.id)) + 1 if not line.id else len(
    #                 wizard.line_ids) + 1
    #             base_pn = wizard.sale_line_id.everest_pn or ''
    #             line.everest_pn = f"{base_pn}.{str(row_index).zfill(2)}"
    #             line.product_id = wizard.sale_line_id.product_id
    #             sale_line_number = wizard.sale_line_id.line_number or 1
    #             line.sub_line_code = f"EVR.{str(sale_line_number).zfill(2)}.{str(row_index).zfill(2)}"

    @api.onchange('billing_percentage')
    def _onchange_billing_percentage(self):
        if not self.wizard_id:
            print("DEBUG: Wizard ID not set yet.")
            return

        sum_other = sum(line.billing_percentage for line in self.wizard_id.line_ids if line.id != self.id)

        if sum_other > 100:
            # self.billing_percentage = 0.0
            raise ValidationError(_(
                "Total Billing Percentage cannot exceed 100%. "
                "Current total would be {:.2f}%".format(sum_other)
            ))