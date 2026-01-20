# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
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


    customer_ref = fields.Char(string='Customer ref')

    # def _collect_affected_root_boms(self):
    #     """
    #     For this recordset of bom.lines return a set of root BOMs that must be
    #     recalculated. This covers:
    #       - the immediate containing BOMs (line.bom_id) and their ancestors (roots)
    #       - if the line has child_bom_id (i.e., it *is* a parent), then also
    #         include roots of that child BOM (because child structure changed)
    #     """
    #     helpers = self.env['cr.mrp.bom.helpers']
    #     affected_roots = set()
    #
    #     for line in self:
    #         # 1) roots for the containing BOM of this line
    #         if line.bom_id:
    #             roots = helpers.get_root_boms_for_bom(line.bom_id)
    #             for r in roots:
    #                 affected_roots.add(r.id)
    #
    #         # 2) if this line itself points to a child BOM, include roots for that child
    #         if line.child_bom_id:
    #             roots_child = helpers.get_root_boms_for_bom(line.child_bom_id)
    #             for r in roots_child:
    #                 affected_roots.add(r.id)
    #
    #     # return browse recordset of root BOMs
    #     return self.env['mrp.bom'].browse(list(affected_roots))
    #
    # @api.model_create_multi
    # def create(self, vals_list):
    #     lines = super().create(vals_list)
    #     roots = lines._collect_affected_root_boms()
    #
    #     for root in roots:
    #         try:
    #             root._assign_branches_for_bom()
    #             # root.with_context(skip_branch_recompute=True)._assign_branches_for_bom()
    #         except Exception:
    #             # log and continue; do not block create
    #             _logger.exception("Error assigning branches for root BOM %s after create", root.id)
    #     return lines
    #
    # def write(self, vals):
    #     # collect roots BEFORE write for lines whose bom_id may change
    #     pre_roots = self._collect_affected_root_boms()
    #     res = super().write(vals)
    #     # collect roots AFTER write (for new relations)
    #     post_roots = self._collect_affected_root_boms()
    #     # union
    #     roots = (pre_roots | post_roots)
    #
    #     for root in roots:
    #         try:
    #             root._assign_branches_for_bom()
    #             # root.with_context(skip_branch_recompute=True)._assign_branches_for_bom()
    #         except Exception:
    #             _logger.exception("Error assigning branches for root BOM %s after write", root.id)
    #
    #     return res
    #
    # def unlink(self):
    #     # collect roots BEFORE unlink (we can't after)
    #     roots = self._collect_affected_root_boms()
    #     res = super().unlink()
    #     for root in roots:
    #         try:
    #             root._assign_branches_for_bom()
    #             # root.with_context(skip_branch_recompute=True)._assign_branches_for_bom()
    #         except Exception:
    #             _logger.exception("Error assigning branches for root BOM %s after unlink", root.id)
    #     return res

    def _collect_affected_root_boms(self):
        """
        For this recordset of bom.lines return a set of root BOMs that must be
        recalculated. Only returns BOMs that are EVR and have project location.
        """
        helpers = self.env['cr.mrp.bom.helpers']
        affected_roots = set()

        for line in self:
            # 1) roots for the containing BOM of this line
            if line.bom_id:
                roots = helpers.get_root_boms_for_bom(line.bom_id)
                for r in roots:
                    # 🔥 ONLY add if it's EVR and has project location
                    if r.is_evr and r.cfe_project_location_id:
                        affected_roots.add(r.id)

            # 2) if this line itself points to a child BOM, include roots for that child
            if line.child_bom_id:
                roots_child = helpers.get_root_boms_for_bom(line.child_bom_id)
                for r in roots_child:
                    # 🔥 ONLY add if it's EVR and has project location
                    if r.is_evr and r.cfe_project_location_id:
                        affected_roots.add(r.id)

        # return browse recordset of root BOMs
        return self.env['mrp.bom'].browse(list(affected_roots))

    @api.model_create_multi
    def create(self, vals_list):
        # 🔥 CREATE WITHOUT triggering branch assignment
        lines = super(MrpBomLine, self.with_context(skip_branch_recompute=True)).create(vals_list)

        # 🔥 THEN trigger branch assignment ONCE for all affected roots
        if not self.env.context.get('skip_branch_recompute'):
            roots = lines._collect_affected_root_boms()
            if roots:
                _logger.info(f"BOM Line Create: Reassigning branches for {len(roots)} root BOMs: {roots.ids}")
                for root in roots:
                    try:
                        root._assign_branches_for_bom()
                    except Exception:
                        _logger.exception(f"Error assigning branches for root BOM {root.id} after create")

        return lines

    # def write(self, vals):
    #     # 🔥 Collect roots BEFORE write
    #     pre_roots = self._collect_affected_root_boms() if not self.env.context.get('skip_branch_recompute') else \
    #     self.env['mrp.bom']
    #
    #     # 🔥 WRITE WITHOUT triggering branch assignment
    #     res = super(MrpBomLine, self.with_context(skip_branch_recompute=True)).write(vals)
    #
    #     # 🔥 Collect roots AFTER write
    #     post_roots = self._collect_affected_root_boms() if not self.env.context.get('skip_branch_recompute') else \
    #     self.env['mrp.bom']
    #
    #     # Union and reassign
    #     roots = (pre_roots | post_roots)
    #     if roots:
    #         _logger.info(f"BOM Line Write: Reassigning branches for {len(roots)} root BOMs: {roots.ids}")
    #         for root in roots:
    #             try:
    #                 root._assign_branches_for_bom()
    #             except Exception:
    #                 _logger.exception(f"Error assigning branches for root BOM {root.id} after write")
    #
    #     return res

    def unlink(self):
        # 🔥 Collect roots BEFORE unlink
        roots = self._collect_affected_root_boms() if not self.env.context.get('skip_branch_recompute') else self.env[
            'mrp.bom']

        # 🔥 UNLINK WITHOUT triggering branch assignment
        res = super(MrpBomLine, self.with_context(skip_branch_recompute=True)).unlink()

        if roots:
            _logger.info(f"BOM Line Unlink: Reassigning branches for {len(roots)} root BOMs: {roots.ids}")
            for root in roots:
                try:
                    root._assign_branches_for_bom()
                except Exception:
                    _logger.exception(f"Error assigning branches for root BOM {root.id} after unlink")

        return res



    def _skip_bom_line(self, product, never_attribute_values=False):
        """Override to pass context when exploding child BOMs"""
        result = super()._skip_bom_line(product,never_attribute_values)

        if result and self.bom_id.is_evr:
            # Pass this line's ID in context for child BOM explosion
            return result.with_context(parent_bom_line_id=self.id)

        return result
