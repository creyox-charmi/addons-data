from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    cr_product_uid = fields.Char(name="Product UID of Gelato", readonly=True)
    lst_price = fields.Float(
        compute="_compute_cr_lst_price",
        inverse="_inverse_cr_product_lst_price",
    )
    list_price = fields.Float(
        compute="_compute_cr_list_price",
        store=True
    )
    cr_fix_price = fields.Float()

    def action_get_gelato_product_info(self):
        # Open the wizard and fetch product details for the selected template
        wizard = self.env['gelato.product.template.wizard'].create({
            'product_uid': self.cr_product_uid,  # assuming you have 'product_uid' in your template
        })

        # Fetch product details from the Gelato API
        wizard.fetch_product_details()

        # Open the wizard view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gelato.product.template.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def open_gelato_price_wizard(self):
        # Get the product UID for the selected product
        product_uid = self.cr_product_uid
        _logger.info(f"Opening Gelato Price Wizard for product: {product_uid}")

        # Open the price wizard and fetch product prices
        wizard = self.env['gelato.product.price.wizard'].create({
            'product_uid': product_uid,
        })

        # Fetch the price data
        wizard.fetch_product_prices(product_uid)

        # Return action to open the wizard
        return {
            'name': 'Gelato Product Price Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'gelato.product.price.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def _inverse_cr_product_lst_price(self):
        Uom = self.env['uom.uom']

        for product in self:
            if self.env.context.get("uom"):
                target_uom = Uom.browse(self.env.context["uom"])
                cr_fix_price = product.uom_id._compute_price(product.lst_price, target_uom)
                _logger.debug("Computed cr_fix_price with UoM: %s → %s", target_uom.display_name, cr_fix_price)
            else:
                cr_fix_price = product.lst_price
                _logger.debug("Used cr_fix_price without UoM: %s", cr_fix_price)

            product.cr_fix_price = cr_fix_price
            _logger.info("Updated cr_fix_price for product %s to %s", product.display_name, cr_fix_price)

            template = product.product_tmpl_id

            if template.product_variant_count == 1:
                template.list_price = cr_fix_price
                _logger.info("Template %s has one variant. Updated list_price to %s", template.display_name,
                             cr_fix_price)
            else:
                other_variants = template.product_variant_ids - product
                all_prices = other_variants.mapped("cr_fix_price") + [product.lst_price]
                min_price = min(all_prices)
                template.with_context(skip_update_fix_price=True).list_price = min_price
                _logger.info("Template %s has multiple variants. Updated list_price to min price %s",
                             template.display_name, min_price)

    def _compute_product_price_extra(self):
        for data in self:
            data.price_extra = 0.0
            _logger.debug("Reset price_extra for variant %s to 0.0", data.display_name)

    @api.depends("cr_fix_price")
    def _compute_cr_lst_price(self):
        uom_uom = self.env["uom.uom"]
        for data in self:
            cr_price = data.cr_fix_price or data.list_price
            if self.env.context.get("uom"):
                ref_uom = uom_uom.browse(self.env.context["uom"])
                cr_price = data.uom_id._compute_price(cr_price, ref_uom)
                _logger.debug("Computed lst_price with UoM: %s → %s", ref_uom.display_name, cr_price)
            else:
                _logger.debug("Computed lst_price without UoM: %s", cr_price)

            data.lst_price = cr_price
            _logger.info("Updated lst_price for %s to %s", data.display_name, cr_price)

    def _compute_cr_list_price(self):
        uom_uom = self.env["uom.uom"]
        for data in self:
            cr_price = data.cr_fix_price or data.product_tmpl_id.list_price
            if self.env.context.get("uom"):
                ref_uom = uom_uom.browse(self.env.context["uom"])
                cr_price = data.uom_id._compute_price(cr_price, ref_uom)
                _logger.debug("Computed list_price with UoM: %s → %s", ref_uom.display_name, cr_price)
            else:
                _logger.debug("Computed list_price without UoM: %s", cr_price)

            data.list_price = cr_price
            _logger.info("Updated list_price for %s to %s", data.display_name, cr_price)

