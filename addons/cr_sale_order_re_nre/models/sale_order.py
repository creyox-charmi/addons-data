# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _check_line_unlink(self):
        non_removable_lines = super()._check_line_unlink()
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.order.line.remove")
        ):
            return non_removable_lines
        else:
            removable_lines = self.filtered(
                lambda line: line.state in ("sale", "done")
                and not line.invoice_lines
                and not line.move_ids.filtered(lambda move: move.state == "done")
            )
            invoiced_lines = self.sudo().filtered(
                lambda line: line.state in ("sale", "done") and line.invoice_lines
            )
            if invoiced_lines:
                raise UserError(
                    _("You can not remove an order line that has been invoiced")
                )
            delivered_lines = self.sudo().filtered(
                lambda line: line.state in ("sale", "done")
                and line.move_ids.filtered(lambda move: move.state == "done")
            )
            if delivered_lines:
                raise UserError(
                    _("You can not remove an order line that has been delivered")
                )
            return non_removable_lines - removable_lines

    def unlink(self):
        non_removable_lines = self._check_line_unlink()
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.order.line.remove")
        ):
            return super().unlink()
        else:
            for line in self - non_removable_lines:
                related_pickings = line.move_ids.mapped("picking_id")
                line.move_ids.filtered(
                    lambda move: move.state not in ("done", "cancel")
                )._action_cancel()
                line.move_ids.filtered(lambda move: move.state != "done").unlink()
                for picking in related_pickings:
                    if not picking.move_ids_without_package:
                        picking.unlink()
            return super().unlink()



from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """On confirmation, update the related product code:
        - If the product has only one variant → update product.template
        - If multiple variants → update product.product
        """
        res = super().action_confirm()

        for order in self:
            _logger.info(f"Confirming Sale Order: {order.name}")

            for line in order.order_line:
                product = line.product_id
                everest_pn = line.everest_pn

                if not product or not everest_pn:
                    _logger.warning(
                        f"Skipping line {line.id}: Missing product or Everest PN "
                        f"(product={bool(product)}, everest_pn={everest_pn})"
                    )
                    continue

                # Determine if the product template has multiple variants
                template = product.product_tmpl_id
                variant_count = len(template.product_variant_ids)

                if variant_count == 1:
                    # Update the product template (single variant case)
                    _logger.info(
                        f"[Single Variant] Updating Template '{template.name}' "
                        f"(ID: {template.id}) default_code -> {everest_pn}"
                    )
                    template.default_code = everest_pn
                else:
                    # Update only this variant (multi-variant case)
                    _logger.info(
                        f"[Multi Variant] Updating Variant '{product.display_name}' "
                        f"(ID: {product.id}) default_code -> {everest_pn}"
                    )
                    product.default_code = everest_pn

        return res

