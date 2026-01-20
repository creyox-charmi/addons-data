from pygments.lexer import default

from odoo import models, fields,api

# class MrpBomLineBranchComponents(models.Model):
#     _name = "mrp.bom.line.branch.components"
#     _description = "Branch mapping per BOM per path"
#
#     bom_line_branch_id = fields.Many2one('mrp.bom.line.branch', string='BOM Line Branch', ondelete='cascade')
#     root_bom_id = fields.Many2one('mrp.bom', string='Root BOM', ondelete='cascade')
#     bom_id = fields.Many2one('mrp.bom',string='Just Child BOM', ondelete='cascade')
#     cr_bom_line_id = fields.Many2one('mrp.bom.line',string='BOM Line', ondelete='cascade', index=True)
#     to_order = fields.Float(string='To Order', default=0.0)
#     to_order_cfe = fields.Float(string='To Order CFE', default=0.0)
#     ordered = fields.Float(string='Ordered', default=0.0)
#     ordered_cfe = fields.Float(string='Ordered CFE', default=0.0)
#     to_transfer = fields.Float(string='To Transfer', default=0.0)
#     to_transfer_cfe = fields.Float(string='To Transfer CFE', default=0.0)
#     transferred = fields.Float(string='Transferred', default=0.0)
#     transferred_cfe = fields.Float(string='Transferred CFE', default=0.0)
#     used = fields.Float(string='Used', default=0.0)
#     is_direct_component = fields.Boolean(string='Is Direct Component',default=False)
#     location_id = fields.Many2one('stock.location',string='Location')
#     free_to_use = fields.Float(
#         string='Free to Use',
#     )

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class MrpBomLineBranchComponents(models.Model):
    _name = "mrp.bom.line.branch.components"
    _description = "Branch components per BOM per path"

    bom_line_branch_id = fields.Many2one('mrp.bom.line.branch', string='BOM Line Branch', ondelete='cascade')
    root_bom_id = fields.Many2one('mrp.bom', string='Root BOM', ondelete='cascade')
    bom_id = fields.Many2one('mrp.bom', string='Just Child BOM', ondelete='cascade')
    cr_bom_line_id = fields.Many2one('mrp.bom.line', string='BOM Line', ondelete='cascade', index=True)
    to_order = fields.Float(string='To Order', default=0.0)
    to_order_cfe = fields.Float(string='To Order CFE', default=0.0)
    ordered = fields.Float(string='Ordered', default=0.0)
    ordered_cfe = fields.Float(string='Ordered CFE', default=0.0)
    to_transfer = fields.Float(string='To Transfer', default=0.0)
    to_transfer_cfe = fields.Float(string='To Transfer CFE', default=0.0)
    transferred = fields.Float(string='Transferred', default=0.0)
    transferred_cfe = fields.Float(string='Transferred CFE', default=0.0)
    used = fields.Float(string='Used', default=0.0)
    is_direct_component = fields.Boolean(string='Is Direct Component', default=False)
    location_id = fields.Many2one('stock.location', string='Location')
    free_to_use = fields.Float(
        string='Free to Use',
        compute='_compute_free_to_use',
        store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity available to use from assigned location if that location (or any ancestor) is marked free."
    )

    @api.model
    def _is_location_marked_free(self, location):
        """
        Return True if `location` or any of its ancestors is 'free'.
        We try these checks in order:
          1) stock.location has boolean field `free_to_use` (custom). Use it if present.
          2) fallback: check location.location_category == 'free'
        """
        if not location:
            return False

        StockLocation = self.env['stock.location'].__class__  # model class
        # safer: check fields dict on model
        location_fields = self.env['stock.location']._fields

        use_boolean_field = 'free_to_use' in location_fields

        cur = location
        while cur:
            if use_boolean_field:
                # prefer explicit boolean field if defined
                try:
                    if bool(cur.free_to_use):
                        return True
                except Exception:
                    # if weird value, ignore and continue up
                    pass
            else:
                # fallback to checking location_category string
                try:
                    if getattr(cur, 'location_category', False) == 'free':
                        return True
                except Exception:
                    pass
            cur = cur.location_id  # go to parent
        return False

    @api.depends('location_id', 'cr_bom_line_id', 'cr_bom_line_id.product_id', 'cr_bom_line_id.product_id.stock_quant_ids', 'cr_bom_line_id.product_id.stock_quant_ids.quantity',
                 'cr_bom_line_id.product_id.stock_quant_ids.location_id', 'cr_bom_line_id.product_id.stock_quant_ids.location_id.location_category')
    def _compute_free_to_use(self):
        StockQuant = self.env['stock.quant']
        for rec in self:
            rec.free_to_use = 0.0
            if not rec.location_id or not rec.cr_bom_line_id or not rec.cr_bom_line_id.product_id:
                # nothing to compute
                continue

            if not self._is_location_marked_free(rec.location_id):
                # the location (nor its parents) are marked free → 0
                rec.free_to_use = 0.0
                continue

            product = rec.cr_bom_line_id.product_id
            # Sum quantities for product under that location (including children)
            domain = [
                ('product_id', '=', product.id),
                ('location_id', 'child_of', rec.location_id.id),
            ]
            # You may want only exact location: replace 'child_of' with '='
            quants = StockQuant.search(domain)
            qty = sum(q.quantity for q in quants)
            rec.free_to_use = float(qty)

    @api.model_create_multi
    def create(self, vals_list):
        """Override to prevent recursive branch assignment"""
        return super(MrpBomLineBranchComponents, self.with_context(skip_branch_recompute=True)).create(vals_list)

    def write(self, vals):
        """Override to prevent recursive branch assignment"""
        return super(MrpBomLineBranchComponents, self.with_context(skip_branch_recompute=True)).write(vals)

    def unlink(self):
        """Override to prevent recursive branch assignment"""
        return super(MrpBomLineBranchComponents, self.with_context(skip_branch_recompute=True)).unlink()



