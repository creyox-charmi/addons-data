# models/mrp_bom.py
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _cron_process_evr_automated_flow(self):
        """Cron job to process all EVR BOMs every 10 minutes"""
        evr_boms = self.search([('is_evr', '=', True)])

        for bom in evr_boms:
            try:
                bom._process_automated_flow()
            except Exception as e:
                _logger.exception(f"Error processing automated flow for BOM {bom.id}: {e}")

        return True

    def _process_automated_flow(self):
        """Process automated flow for this root BOM"""
        self.ensure_one()

        if not self.is_evr:
            return

        # Initialize cache for this root BOM
        if not hasattr(self.__class__, '_flow_branch_cache'):
            self.__class__._flow_branch_cache = {}

        cache_key = f"flow_bom_{self.id}"
        self.__class__._flow_branch_cache[cache_key] = {
            'assignments': {},
            'seen_paths': []
        }

        try:
            # Process all lines in the BOM tree with parent branch context
            self._process_bom_lines_recursive(
                bom=self,
                parent_branch_location=self.cfe_project_location_id,
                index="0",
                level=0
            )
        finally:
            # Clean up cache
            if cache_key in self.__class__._flow_branch_cache:
                del self.__class__._flow_branch_cache[cache_key]


    # def _process_bom_lines_recursive(self, bom, parent_branch_location, index="0", level=0, parent_qty=1.0):
    #     """Recursively process all BOM lines with parent branch context and quantity multiplier"""
    #     FlowProcessor = self.env['mrp.bom.automated.flow.processor']
    #
    #     for line_idx, line in enumerate(bom.bom_line_ids):
    #         line_index = f"{index}{line_idx}"
    #
    #         # Calculate accumulated quantity
    #         line_qty = float(line.product_qty or 1.0) * parent_qty
    #
    #         # Determine this line's branch location
    #         if line.child_bom_id:
    #             # This line has a child BOM - get its branch from root BOM context
    #             branch = self._get_branch_for_line_with_cache(line, line_index)
    #             current_branch_location = branch.location_id if branch else parent_branch_location
    #         else:
    #             # Normal line (no child BOM) - use parent's branch
    #             current_branch_location = parent_branch_location
    #             branch = False
    #
    #         # Only process lines with both approvals
    #         if line.approval_1 and line.approval_2:
    #             FlowProcessor.process_line(
    #                 root_bom=self,
    #                 bom_line=line,
    #                 branch_location=current_branch_location,
    #                 accumulated_qty=line_qty  # Pass accumulated quantity
    #             )
    #
    #         # Recurse into child BOM if exists
    #         if line.child_bom_id:
    #             self._process_bom_lines_recursive(
    #                 bom=line.child_bom_id,
    #                 parent_branch_location=current_branch_location,
    #                 index=line_index,
    #                 level=level + 1,
    #                 parent_qty=line_qty  # Pass accumulated quantity to children
    #             )

    # models/mrp_bom.py - Update _process_bom_lines_recursive
    def _process_bom_lines_recursive(self, bom, parent_branch_location, index="0", level=0, parent_qty=1.0):
        """Recursively process all BOM lines with parent branch context and quantity multiplier"""
        FlowProcessor = self.env['mrp.bom.automated.flow.processor']
        Branch = self.env['mrp.bom.line.branch']

        for line_idx, line in enumerate(bom.bom_line_ids):
            line_index = f"{index}{line_idx}"
            line_qty = float(line.product_qty or 1.0) * parent_qty

            if line.child_bom_id:
                branch = self._get_branch_for_line_with_cache(line, line_index)
                current_branch_location = branch.location_id if branch else parent_branch_location
                branch_record = branch
            else:
                current_branch_location = parent_branch_location
                # Find branch record for normal line using parent path
                parent_index = index[:-1] if len(index) > 1 else "0"
                parent_line_id = int(index[-1]) if len(index) > 1 else None

                if parent_line_id is not None:
                    parent_line = bom.bom_line_ids[parent_line_id] if parent_line_id < len(bom.bom_line_ids) else None
                    if parent_line:
                        branch_record = Branch.search([
                            ('bom_id', '=', self.id),
                            ('bom_line_id', '=', parent_line.id)
                        ], order='sequence', limit=1)
                    else:
                        branch_record = False
                else:
                    branch_record = False

            if line.approval_1 and line.approval_2 and branch_record:
                FlowProcessor.process_line(
                    root_bom=self,
                    bom_line=line,
                    branch_record=branch_record,
                    accumulated_qty=line_qty
                )

            if line.child_bom_id:
                self._process_bom_lines_recursive(
                    bom=line.child_bom_id,
                    parent_branch_location=current_branch_location,
                    index=line_index,
                    level=level + 1,
                    parent_qty=line_qty
                )

    def _get_branch_for_line_with_cache(self, bom_line, index):
        """
        Get branch location for a BOM line in context of this root BOM
        Uses cache to handle duplicate bom_line_ids at different paths
        """
        Branch = self.env['mrp.bom.line.branch']

        # Get all branches for this bom_line
        branches = Branch.search([
            ('bom_id', '=', self.id),
            ('bom_line_id', '=', bom_line.id)
        ], order='sequence')

        if not branches:
            return False

        if len(branches) == 1:
            return branches[0]

        # Multiple branches - use cache to determine which one
        cache_key = f"flow_bom_{self.id}"

        if not hasattr(self.__class__, '_flow_branch_cache'):
            return branches[0]

        cache = self.__class__._flow_branch_cache.get(cache_key)
        if not cache:
            return branches[0]

        path_key = f"{self.id}_{bom_line.id}_{index}"

        if path_key not in cache['seen_paths']:
            # First time seeing this path
            existing_count = len([p for p in cache['seen_paths']
                                  if p.startswith(f"{self.id}_{bom_line.id}_")])

            if existing_count < len(branches):
                branch = branches[existing_count]
            else:
                branch = branches[-1]

            cache['assignments'][path_key] = branch.id
            cache['seen_paths'].append(path_key)
        else:
            # Path already seen, reuse assignment
            branch_id = cache['assignments'].get(path_key)
            branch = Branch.browse(branch_id)

        return branch