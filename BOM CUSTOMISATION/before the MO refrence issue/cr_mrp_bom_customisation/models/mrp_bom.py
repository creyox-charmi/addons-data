# models/mrp_bom.py
from odoo import models, fields, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    is_evr = fields.Boolean(
        string='Is EVR',
        default=False,
        help="Indicates if this BOM is for EVR products"
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set is_evr based on product default_code"""
        for vals in vals_list:
            if 'product_tmpl_id' in vals or 'product_id' in vals:
                self._set_is_evr_from_product(vals)
        return super().create(vals_list)

    def write(self, vals):
        """Override write to update is_evr when product changes"""
        if 'product_tmpl_id' in vals or 'product_id' in vals:
            self._set_is_evr_from_product(vals)
        return super().write(vals)

    def _set_is_evr_from_product(self, vals):
        """Set is_evr based on product internal reference"""
        product = None

        if 'product_id' in vals and vals['product_id']:
            product = self.env['product.product'].browse(vals['product_id'])
        elif 'product_tmpl_id' in vals and vals['product_tmpl_id']:
            product_tmpl = self.env['product.template'].browse(vals['product_tmpl_id'])
            if product_tmpl.product_variant_count == 1:
                product = product_tmpl.product_variant_ids[0]

        if product and product.default_code:
            vals['is_evr'] = product.default_code.startswith('EVR')
        else:
            vals['is_evr'] = False

    @api.onchange('product_tmpl_id', 'product_id')
    def _onchange_product_set_is_evr(self):
        """Update is_evr when product is changed in the form"""
        product = self.product_id or (
            self.product_tmpl_id.product_variant_ids[0]
            if self.product_tmpl_id and self.product_tmpl_id.product_variant_count == 1
            else None
        )

        if product and product.default_code:
            self.is_evr = product.default_code.startswith('EVR')
        else:
            self.is_evr = False