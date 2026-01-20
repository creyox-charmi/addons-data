# models/mrp_bom_line.py
from odoo import models, api,fields
import logging

_logger = logging.getLogger(__name__)
class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    approve_to_manufacture = fields.Boolean(
        string='Approve to Manufacture',
        default=False,
        help="If checked, MO will be created for this BOM line"
    )

    to_order = fields.Float(
        string='To Order',
        compute='_compute_purchase_fields',
        store=False
    )

    to_order_cfe = fields.Float(
        string='To Order CFE',
        compute='_compute_purchase_fields',
        store=False
    )

    ordered = fields.Float(
        string='Ordered',
        compute='_compute_purchase_fields',
        store=False
    )

    ordered_cfe = fields.Float(
        string='Ordered CFE',
        compute='_compute_purchase_fields',
        store=False
    )

    to_transfer = fields.Float(
        string='To Transfer',
        compute='_compute_purchase_fields',
        store=False
    )

    to_transfer_cfe = fields.Float(
        string='To Transfer CFE',
        compute='_compute_purchase_fields',
        store=False
    )

    transferred = fields.Float(
        string='Transferred',
        compute='_compute_purchase_fields',
        store=False
    )

    transferred_cfe = fields.Float(
        string='Transferred CFE',
        compute='_compute_purchase_fields',
        store=False
    )

    used = fields.Float(
        string='Used',
        compute='_compute_purchase_fields',
        store=False
    )

    free_to_use = fields.Float(
        string='Free to Use',
        compute='_compute_free_to_use',
    )

    customer_ref = fields.Char(string='Customer ref')

    @api.depends('approval_1', 'approval_2', 'lli', 'product_id', 'cfe_quantity')
    def _compute_purchase_fields(self):
        for line in self:
            if line.approval_1 and line.approval_2:
                line.to_order = 0.0
                line.to_order_cfe = 0.0
                line.ordered = 0.0
                line.ordered_cfe = 0.0
                line.to_transfer = 0.0
                line.to_transfer_cfe = 0.0
                line.transferred = 0.0
                line.transferred_cfe = 0.0
                line.used = 0.0
            else:
                line.to_order = False
                line.to_order_cfe = False
                line.ordered = False
                line.ordered_cfe = False
                line.to_transfer = False
                line.to_transfer_cfe = False
                line.transferred = False
                line.transferred_cfe = False
                line.used = False

    @api.depends('product_id')
    def _compute_free_to_use(self):
        print('=============================>>>>>>>>>>>>>>>>>>>>>>')
        for line in self:
            if line.product_id:
                # Get all free locations
                free_locations = self.env['stock.location'].search([
                    ('location_category', '=', 'free'),
                    ('usage', '=', 'internal')
                ])

                if free_locations:
                    # Get stock quantity for this product in free locations
                    stock_quants = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id', 'in', free_locations.ids)
                    ])

                    line.free_to_use = sum(stock_quants.mapped('quantity'))
                    print('free_to_use : ',line , ' ' ,line.free_to_use)
                else:
                    line.free_to_use = 0.0
            else:
                line.free_to_use = 0.0

    def _collect_affected_root_boms(self):
        """
        For this recordset of bom.lines return a set of root BOMs that must be
        recalculated. This covers:
          - the immediate containing BOMs (line.bom_id) and their ancestors (roots)
          - if the line has child_bom_id (i.e., it *is* a parent), then also
            include roots of that child BOM (because child structure changed)
        """
        helpers = self.env['cr.mrp.bom.helpers']
        affected_roots = set()

        for line in self:
            # 1) roots for the containing BOM of this line
            if line.bom_id:
                roots = helpers.get_root_boms_for_bom(line.bom_id)
                for r in roots:
                    affected_roots.add(r.id)

            # 2) if this line itself points to a child BOM, include roots for that child
            if line.child_bom_id:
                roots_child = helpers.get_root_boms_for_bom(line.child_bom_id)
                for r in roots_child:
                    affected_roots.add(r.id)

        # return browse recordset of root BOMs
        return self.env['mrp.bom'].browse(list(affected_roots))

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        roots = lines._collect_affected_root_boms()
        # call assign on each root (avoid recursion contexts)
        for root in roots:
            try:
                root.with_context(skip_branch_recompute=True)._assign_branches_for_bom(root)
            except Exception:
                # log and continue; do not block create
                _logger.exception("Error assigning branches for root BOM %s after create", root.id)
        return lines

    def write(self, vals):
        # collect roots BEFORE write for lines whose bom_id may change
        pre_roots = self._collect_affected_root_boms()
        res = super().write(vals)
        # collect roots AFTER write (for new relations)
        post_roots = self._collect_affected_root_boms()
        # union
        roots = (pre_roots | post_roots)
        for root in roots:
            try:
                root.with_context(skip_branch_recompute=True)._assign_branches_for_bom(root)
            except Exception:
                _logger.exception("Error assigning branches for root BOM %s after write", root.id)

        # if vals.get('approve_to_manufacture') is True:
        #     for line in self:
        #
        #         # Find related MOs created from this line's child BOM
        #         mos = self.env['mrp.production'].search([
        #             ('bom_id', '=', line.child_bom_id.id),
        #             ('root_bom_id', '=', line.bom_id.id),
        #         ])
        #
        #         for mo in mos:
        #             if mo.state == 'draft':
        #                 mo.action_confirm()
        #
        #                 # Send Notification using bus.bus
        #                 self.env['bus.bus']._sendone(
        #                     self.env.user.partner_id,
        #                     "simple_notification",
        #                     {
        #                         "title": "MO Confirmed",
        #                         "message": (
        #                             f"MO {mo.name} confirmed for "
        #                             f"{line.child_bom_id.display_name}"
        #                         ),
        #                         "sticky": False,
        #                         "type": "success",
        #                     },
        #                 )

        return res

    def unlink(self):
        # collect roots BEFORE unlink (we can't after)
        roots = self._collect_affected_root_boms()
        res = super().unlink()
        for root in roots:
            try:
                root.with_context(skip_branch_recompute=True)._assign_branches_for_bom(root)
            except Exception:
                _logger.exception("Error assigning branches for root BOM %s after unlink", root.id)
        return res

    def _skip_bom_line(self, product, never_attribute_values=False):
        """Override to pass context when exploding child BOMs"""
        result = super()._skip_bom_line(product,never_attribute_values)

        if result and self.bom_id.is_evr:
            # Pass this line's ID in context for child BOM explosion
            return result.with_context(parent_bom_line_id=self.id)

        return result
