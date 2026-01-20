# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
import uuid

from odoo import models, api, _
import logging

from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


def _generate_branch_codes():
    codes = []
    for c in range(ord('A'), ord('Z') + 1):
        codes.append(chr(c))
    for c in range(ord('A'), ord('Z') + 1):
        for d in range(1, 10):
            codes.append(f"{chr(c)}{d}")
    for c1 in range(ord('A'), ord('Z') + 1):
        for c2 in range(ord('A'), ord('Z') + 1):
            codes.append(chr(c1) + chr(c2))
    return codes


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    # def create(self, vals_list):
    #     _logger.info("=== BOM CREATE called ===")
    #     boms = super().create(vals_list)
    #
    #     for bom in boms:
    #         _logger.info(f"Created BOM {bom.id}, is_evr: {bom.is_evr}")
    #
    #         # Skip if not EVR
    #         if not bom.is_evr:
    #             continue
    #
    #         # Check project
    #         project = bom.project_id
    #
    #         if not project:
    #             continue
    #
    #         # parent: Project Location
    #         parent_loc = bom._find_project_parent_location()
    #
    #         loc_name = project.name
    #
    #         Location = self.env['stock.location']
    #
    #         # Check existing location
    #         existing = Location.search([
    #             ('name', '=', loc_name),
    #             ('location_id', '=', parent_loc.id),
    #             ('usage', '=', 'internal')
    #         ], limit=1)
    #
    #         if existing:
    #             bom.cfe_project_location_id = existing.id
    #             continue
    #
    #         # Create new location
    #         new_loc = Location.create({
    #             'name': loc_name,
    #             'location_id': parent_loc.id,
    #             'usage': 'internal',
    #         })
    #
    #         # Assign to BOM
    #         bom.cfe_project_location_id = new_loc.id
    #
    #     # -----------------------------------------------------
    #     #  PART 2 — RECURSIVE MO CREATION
    #     # -----------------------------------------------------
    #     for bom in boms:
    #         if bom.is_evr:
    #             bom.action_create_child_mos_recursive()
    #
    #     return boms

    def check_all_components_approved(self, processed_boms=None):
        """
        Recursively check if all BOM components are approved to manufacture.
        Returns (is_approved, unapproved_products) tuple.
        """
        if processed_boms is None:
            processed_boms = set()

        # Prevent infinite loops in case of circular BOM references
        if self.id in processed_boms:
            return True, []

        processed_boms.add(self.id)
        unapproved_products = []

        for bom_line in self.bom_line_ids:
            # Check if this line has a BOM
            component_bom = self.env['mrp.bom']._bom_find(
                bom_line.product_id,
                bom_type='normal'
            )[bom_line.product_id]

            if component_bom:
                # This component has a BOM
                if not bom_line.approve_to_manufacture:
                    unapproved_products.append({
                        'product': bom_line.product_id.display_name,
                        'level': 'current'
                    })

                # Recursively check sub-components
                is_approved, sub_unapproved = component_bom.check_all_components_approved(
                    processed_boms.copy()
                )

                if not is_approved:
                    unapproved_products.extend(sub_unapproved)

        is_all_approved = len(unapproved_products) == 0
        return is_all_approved, unapproved_products

    def check_bom_components_approval(self):
        """
        Public method to be called from JavaScript.
        Returns dict with approval status and unapproved products.
        """
        self.ensure_one()
        is_approved, unapproved_products = self.check_all_components_approved()

        return {
            'approved': is_approved,
            'unapproved_products': unapproved_products
        }

    def write(self, vals):
        res = super().write(vals)

        for bom in self:
            # Only run if:
            # - is_evr becomes True
            # - OR project_id changed
            if not bom.is_evr:
                continue

            if 'project_id' not in vals and 'is_evr' not in vals:
                continue

            project = bom.project_id

            if not project:
                continue

            parent_loc = bom._find_project_parent_location()

            loc_name = project.name

            Location = self.env['stock.location']

            # Find existing
            existing = Location.search([
                ('name', '=', loc_name),
                ('location_id', '=', parent_loc.id),
                ('usage', '=', 'internal')
            ], limit=1)

            if existing:
                bom.cfe_project_location_id = existing.id
                continue

            new_loc = Location.create({
                'name': loc_name,
                'location_id': parent_loc.id,
                'usage': 'internal',
            })

            bom.cfe_project_location_id = new_loc.id

        return res

    # def _assign_branches_for_bom(self):
    #     """
    #     Assign branch codes for each root BOM in `self`.
    #     Uses path-based unique branch creation and ALSO creates stock.locations
    #     same as old code.
    #     """
    #     Branch = self.env['mrp.bom.line.branch']
    #     codes = _generate_branch_codes()
    #
    #     for root_bom in self:
    #
    #         if self.env.context.get('skip_branch_recompute'):
    #             continue
    #
    #         # remove previous mappings for this root
    #         old = Branch.search([('bom_id', '=', root_bom.id)])
    #         if old:
    #             old.unlink()
    #
    #         idx = 0  # start assigning from A
    #
    #         # DFS
    #         def dfs(current_bom):
    #             nonlocal idx
    #
    #             lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))
    #
    #             for line in lines:
    #
    #                 if line.child_bom_id:
    #
    #                     if idx >= len(codes):
    #                         raise UserError("No more branch codes available.")
    #
    #                     code = codes[idx]
    #                     idx += 1
    #
    #                     # UNIQUE ID for this occurrence
    #                     path_uid = uuid.uuid4().hex
    #
    #                     # 📌 LOCATION CREATION ADDED HERE (same as old code)
    #                     # project_parent = self._find_project_parent_location_of_root_bom(root_bom)
    #                     project_parent = self.cfe_project_location_id
    #
    #                     loc = self.env['stock.location'].create({
    #                         'name': code,  # OR f"{root_bom.display_name}-{code}"
    #                         'location_id': project_parent.id,
    #                         'usage': 'internal',
    #                     })
    #
    #                     branch = Branch.create({
    #                         'bom_id': root_bom.id,
    #                         'bom_line_id': line.id,
    #                         'branch_name': code,
    #                         'sequence': idx,
    #                         'path_uid': path_uid,
    #                         'location_id': loc.id,
    #                     })
    #
    #                     Component = self.env['mrp.bom.line.branch.components']
    #
    #                     child_bom = line.child_bom_id
    #
    #                     if child_bom:
    #                         for child_line in child_bom.bom_line_ids:
    #                             if not child_line.child_bom_id:
    #                                 Component.create({
    #                                     'bom_line_branch_id': branch.id,
    #                                     'root_bom_id': branch.bom_id.id,
    #                                     'bom_id': child_bom.id,
    #                                     'cr_bom_line_id': child_line.id,
    #                                     'location_id':branch.location_id.id,
    #                                 })
    #
    #                     # now go deeper
    #                     dfs(line.child_bom_id)
    #
    #                 else:
    #                     print(f"  Leaf line {line.id} → no mapping")
    #
    #         dfs(root_bom)
    #
    #         Component = self.env['mrp.bom.line.branch.components']
    #
    #         root_leaf_lines = root_bom.bom_line_ids.filtered(lambda l: not l.child_bom_id)
    #         print(f"Assigning root components  {len(root_leaf_lines)} ")
    #
    #         for cr_line in root_leaf_lines:
    #
    #             comp = Component.create({
    #                 'root_bom_id': root_bom.id,
    #                 'bom_id': root_bom.id,
    #                 'cr_bom_line_id': cr_line.id,
    #                 'is_direct_component':True,
    #                 'location_id':root_bom.cfe_project_location_id.id,
    #             })
    #
    #             print(f"Components create for {comp}: {comp.root_bom_id.id}")
    #
    #
    #         total_assigned = Branch.search_count([('bom_id', '=', root_bom.id)])
    #
    #     return True

    # def _assign_branches_for_bom(self):
    #     """
    #     Assign branch codes for each root BOM in `self`.
    #     Uses path-based unique branch creation and ALSO creates stock.locations
    #     same as old code.
    #     """
    #     Branch = self.env['mrp.bom.line.branch']
    #     Component = self.env['mrp.bom.line.branch.components']
    #     codes = _generate_branch_codes()
    #
    #     for root_bom in self:
    #
    #         if self.env.context.get('skip_branch_recompute'):
    #             continue
    #
    #         # Ensure root_bom has cfe_project_location_id before starting
    #         if not root_bom.cfe_project_location_id:
    #             _logger.warning(f"Root BOM {root_bom.id} has no cfe_project_location_id. Skipping branch assignment.")
    #             continue
    #
    #         # Store root location ID
    #         root_location_id = root_bom.cfe_project_location_id.id
    #
    #         # remove previous mappings for this root
    #         old = Branch.search([('bom_id', '=', root_bom.id)])
    #         print('old : ',old)
    #         if old:
    #             old.unlink()
    #
    #         idx = 0  # start assigning from A
    #
    #         # DFS
    #         def dfs(current_bom, parent_location_id):
    #             nonlocal idx
    #
    #             lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))
    #
    #             for line in lines:
    #
    #                 if line.child_bom_id:
    #
    #                     if idx >= len(codes):
    #                         raise UserError("No more branch codes available.")
    #
    #                     code = codes[idx]
    #                     idx += 1
    #
    #                     path_uid = uuid.uuid4().hex
    #
    #                     # Create location as sublocation of parent
    #                     loc = self.env['stock.location'].create({
    #                         'name': code,
    #                         'location_id': parent_location_id,
    #                         'usage': 'internal',
    #                     })
    #
    #                     branch = Branch.create({
    #                         'bom_id': root_bom.id,
    #                         'bom_line_id': line.id,
    #                         'branch_name': code,
    #                         'sequence': idx,
    #                         'path_uid': path_uid,
    #                         'location_id': loc.id,
    #                     })
    #
    #                     child_bom = line.child_bom_id
    #
    #                     if child_bom:
    #                         for child_line in child_bom.bom_line_ids:
    #                             if not child_line.child_bom_id:
    #                                 Component.create({
    #                                     'bom_line_branch_id': branch.id,
    #                                     'root_bom_id': root_bom.id,
    #                                     'bom_id': child_bom.id,
    #                                     'cr_bom_line_id': child_line.id,
    #                                     'location_id': loc.id,
    #                                 })
    #
    #                     # Recurse with current branch location
    #                     dfs(line.child_bom_id, loc.id)
    #
    #                 else:
    #                     print(f"  Leaf line {line.id} → no mapping")
    #
    #         # Start DFS with root_bom's cfe_project_location_id
    #         dfs(root_bom, root_location_id)
    #
    #         # Create components for root-level leaf lines
    #         root_leaf_lines = root_bom.bom_line_ids.filtered(lambda l: not l.child_bom_id)
    #         print(f"Assigning root components  {len(root_leaf_lines)} ")
    #
    #         for cr_line in root_leaf_lines:
    #             comp = Component.create({
    #                 'root_bom_id': root_bom.id,
    #                 'bom_id': root_bom.id,
    #                 'cr_bom_line_id': cr_line.id,
    #                 'is_direct_component': True,
    #                 'location_id': root_location_id,
    #             })
    #
    #             print(f"Components create for {comp}: {comp.root_bom_id.id}")
    #
    #         total_assigned = Branch.search_count([('bom_id', '=', root_bom.id)])
    #         print('total_assigned : ',total_assigned)
    #     return True

    # def _assign_branches_for_bom(self):
    #     """
    #     Assign branch codes for each root BOM in `self`.
    #     Uses path-based unique branch creation and ALSO creates stock.locations
    #     same as old code.
    #     """
    #     Branch = self.env['mrp.bom.line.branch']
    #     Component = self.env['mrp.bom.line.branch.components']
    #     codes = _generate_branch_codes()
    #
    #     for root_bom in self:
    #
    #         if self.env.context.get('skip_branch_recompute'):
    #             continue
    #
    #         # Ensure root_bom has cfe_project_location_id before starting
    #         if not root_bom.cfe_project_location_id:
    #             _logger.warning(f"Root BOM {root_bom.id} has no cfe_project_location_id. Skipping branch assignment.")
    #             continue
    #
    #         # Store root location ID
    #         root_location_id = root_bom.cfe_project_location_id.id
    #
    #         # remove previous mappings for this root (components will cascade delete)
    #         old_branches = Branch.search([('bom_id', '=', root_bom.id)])
    #         old_components = Component.search([('root_bom_id', '=', root_bom.id)])
    #
    #         if old_branches:
    #             old_branches.unlink()
    #         if old_components:
    #             old_components.unlink()
    #
    #         idx = 0  # start assigning from A
    #
    #         # DFS
    #         def dfs(current_bom, parent_location_id):
    #             nonlocal idx
    #
    #             lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))
    #
    #             for line in lines:
    #
    #                 if line.child_bom_id:
    #
    #                     if idx >= len(codes):
    #                         raise UserError("No more branch codes available.")
    #
    #                     code = codes[idx]
    #                     idx += 1
    #
    #                     path_uid = uuid.uuid4().hex
    #
    #                     # Create location as sublocation of parent
    #                     loc = self.env['stock.location'].create({
    #                         'name': code,
    #                         'location_id': parent_location_id,
    #                         'usage': 'internal',
    #                     })
    #
    #                     branch = Branch.create({
    #                         'bom_id': root_bom.id,
    #                         'bom_line_id': line.id,
    #                         'branch_name': code,
    #                         'sequence': idx,
    #                         'path_uid': path_uid,
    #                         'location_id': loc.id,
    #                     })
    #
    #                     child_bom = line.child_bom_id
    #
    #                     # Create component records for all leaf lines in this branch
    #                     if child_bom:
    #                         for child_line in child_bom.bom_line_ids:
    #                             if not child_line.child_bom_id:
    #                                 Component.create({
    #                                     'bom_line_branch_id': branch.id,
    #                                     'root_bom_id': root_bom.id,
    #                                     'bom_id': child_bom.id,
    #                                     'cr_bom_line_id': child_line.id,
    #                                     'location_id': loc.id,
    #                                     'is_direct_component': False,
    #                                 })
    #
    #                         # Recurse with current branch location
    #                         dfs(line.child_bom_id, loc.id)
    #
    #         # Start DFS with root_bom's cfe_project_location_id
    #         dfs(root_bom, root_location_id)
    #
    #         # Create components for root-level leaf lines
    #         root_leaf_lines = root_bom.bom_line_ids.filtered(lambda l: not l.child_bom_id)
    #
    #         for cr_line in root_leaf_lines:
    #             Component.create({
    #                 'root_bom_id': root_bom.id,
    #                 'bom_id': root_bom.id,
    #                 'cr_bom_line_id': cr_line.id,
    #                 'is_direct_component': True,
    #                 'location_id': root_location_id,
    #             })
    #
    #         total_branches = Branch.search_count([('bom_id', '=', root_bom.id)])
    #         total_components = Component.search_count([('root_bom_id', '=', root_bom.id)])
    #         _logger.info(f"BOM {root_bom.id}: Created {total_branches} branches and {total_components} components")
    #
    #     return True

    # In mrp_bom.py

    # In mrp_bom.py

    def create(self, vals_list):
        # CREATE WITHOUT triggering branch assignment from BOM lines
        boms = super(MrpBom, self.with_context(skip_branch_recompute=True)).create(vals_list)

        _logger.info(f"=== BOM CREATE called ===")

        for bom in boms:
            # Skip if not EVR
            if not bom.is_evr:
                _logger.info(f"BOM {bom.id} is not EVR, skipping")
                continue

            # Check project
            project = bom.project_id
            if not project:
                _logger.info(f"BOM {bom.id} has no project, skipping")
                continue

            # parent: Project Location
            parent_loc = bom._find_project_parent_location()
            loc_name = project.name
            Location = self.env['stock.location']

            # Check existing location
            existing = Location.search([
                ('name', '=', loc_name),
                ('location_id', '=', parent_loc.id),
                ('usage', '=', 'internal')
            ], limit=1)

            if existing:
                bom.cfe_project_location_id = existing.id
                _logger.info(f"BOM {bom.id}: Using existing location {existing.id} - {existing.name}")
            else:
                # Create new location
                new_loc = Location.create({
                    'name': loc_name,
                    'location_id': parent_loc.id,
                    'usage': 'internal',
                })
                bom.cfe_project_location_id = new_loc.id
                _logger.info(f"BOM {bom.id}: Created new location {new_loc.id} - {new_loc.name}")

        _logger.info(f"Created {len(boms.filtered('is_evr'))} BOM records with EVR status")

        # 🔥 NOW assign branches for all EVR BOMs with project location
        # 🔥 IMPORTANT: Remove skip_branch_recompute context before calling _assign_branches_for_bom
        evr_boms_with_location = boms.filtered(lambda b: b.is_evr and b.cfe_project_location_id)

        if evr_boms_with_location:
            _logger.info(f"Assigning branches for {len(evr_boms_with_location)} EVR BOMs: {evr_boms_with_location.ids}")
            for bom in evr_boms_with_location:
                try:
                    _logger.info(f"Starting branch assignment for BOM {bom.id}")
                    # 🔥 Call WITHOUT the skip context
                    bom.with_context(skip_branch_recompute=False)._assign_branches_for_bom()
                    _logger.info(f"Completed branch assignment for BOM {bom.id}")
                except Exception as e:
                    _logger.exception(f"Error assigning branches for BOM {bom.id}: {str(e)}")

        # Verify branches were created before creating MOs
        for bom in evr_boms_with_location:
            branch_count = self.env['mrp.bom.line.branch'].search_count([('bom_id', '=', bom.id)])
            _logger.info(f"BOM {bom.id} has {branch_count} branches assigned")

            if branch_count == 0:
                _logger.warning(f"BOM {bom.id} has no branches! Skipping MO creation")
                continue

            try:
                _logger.info(f"Starting MO creation for BOM {bom.id}")
                bom.action_create_child_mos_recursive()
                _logger.info(f"Completed MO creation for BOM {bom.id}")
            except Exception as e:
                _logger.exception(f"Error creating MOs for BOM {bom.id}: {str(e)}")

        _logger.info(f"=== BOM CREATE completed ===")
        return boms

    def _assign_branches_for_bom(self):
        """
        Assign branch codes for each root BOM in `self`.
        """
        Branch = self.env['mrp.bom.line.branch']
        Component = self.env['mrp.bom.line.branch.components']
        codes = _generate_branch_codes()

        for root_bom in self:
            _logger.info(f"Processing branch assignment for BOM {root_bom.id}")

            if self.env.context.get('skip_branch_recompute'):
                _logger.info(f"BOM {root_bom.id}: Skipping due to context flag")
                continue

            # Ensure root_bom has cfe_project_location_id before starting
            if not root_bom.cfe_project_location_id:
                _logger.warning(f"Root BOM {root_bom.id} has no cfe_project_location_id. Skipping branch assignment.")
                continue

            _logger.info(
                f"BOM {root_bom.id}: Project location = {root_bom.cfe_project_location_id.id} - {root_bom.cfe_project_location_id.name}")

            # Store root location ID
            root_location_id = root_bom.cfe_project_location_id.id

            # Delete old branches/components
            old_branches = Branch.search([('bom_id', '=', root_bom.id)])
            old_components = Component.search([('root_bom_id', '=', root_bom.id)])

            if old_branches:
                _logger.info(f"Deleting {len(old_branches)} old branches for BOM {root_bom.id}")
                old_branches.unlink()
            if old_components:
                _logger.info(f"Deleting {len(old_components)} old components for BOM {root_bom.id}")
                old_components.unlink()

            idx = 0
            created_branches = []
            created_components = []

            _logger.info(f"BOM {root_bom.id}: Starting DFS traversal, has {len(root_bom.bom_line_ids)} lines")

            # DFS
            def dfs(current_bom, parent_location_id, depth=0):
                nonlocal idx
                indent = "  " * depth

                lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))
                _logger.info(f"{indent}DFS: BOM {current_bom.id} has {len(lines)} lines at depth {depth}")

                for line in lines:
                    _logger.info(f"{indent}  Processing line {line.id}: {line.product_id.display_name}")

                    if line.child_bom_id:
                        _logger.info(f"{indent}    Line has child BOM {line.child_bom_id.id}")

                        if idx >= len(codes):
                            raise UserError("No more branch codes available.")

                        code = codes[idx]
                        idx += 1

                        path_uid = uuid.uuid4().hex

                        # Create location as sublocation of parent
                        loc = self.env['stock.location'].create({
                            'name': code,
                            'location_id': parent_location_id,
                            'usage': 'internal',
                        })
                        _logger.info(f"{indent}    Created location {loc.id}: {code}")

                        # Create branch
                        branch = Branch.create({
                            'bom_id': root_bom.id,
                            'bom_line_id': line.id,
                            'branch_name': code,
                            'sequence': idx,
                            'path_uid': path_uid,
                            'location_id': loc.id,
                        })
                        created_branches.append(branch.id)
                        _logger.info(f"{indent}    Created branch {branch.id}: {code} for line {line.id}")

                        child_bom = line.child_bom_id

                        # Create component records for all leaf lines in this branch
                        if child_bom:
                            leaf_lines = child_bom.bom_line_ids.filtered(lambda l: not l.child_bom_id)
                            _logger.info(f"{indent}    Child BOM has {len(leaf_lines)} leaf components")

                            for child_line in leaf_lines:
                                comp = Component.create({
                                    'bom_line_branch_id': branch.id,
                                    'root_bom_id': root_bom.id,
                                    'bom_id': child_bom.id,
                                    'cr_bom_line_id': child_line.id,
                                    'location_id': loc.id,
                                    'is_direct_component': False,
                                })
                                created_components.append(comp.id)
                                _logger.info(
                                    f"{indent}      Created component {comp.id} for {child_line.product_id.display_name}")

                            # Recurse with current branch location
                            dfs(line.child_bom_id, parent_location_id)
                    else:
                        _logger.info(f"{indent}    Line is a leaf (no child BOM)")

            # Start DFS with root_bom's cfe_project_location_id
            dfs(root_bom, root_location_id)

            # Create components for root-level leaf lines
            root_leaf_lines = root_bom.bom_line_ids.filtered(lambda l: not l.child_bom_id)
            _logger.info(f"BOM {root_bom.id}: Creating {len(root_leaf_lines)} root-level leaf components")

            for cr_line in root_leaf_lines:
                comp = Component.create({
                    'root_bom_id': root_bom.id,
                    'bom_id': root_bom.id,
                    'cr_bom_line_id': cr_line.id,
                    'is_direct_component': True,
                    'location_id': root_location_id,
                })
                created_components.append(comp.id)
                _logger.info(f"  Created root leaf component {comp.id} for {cr_line.product_id.display_name}")

            _logger.info(
                f"BOM {root_bom.id}: ✓ Created {len(created_branches)} branches and {len(created_components)} components")

        return True



    # def action_assign_branches(self):
    #     for bom in self:
    #         bom._assign_branches_for_bom()
    #     return True

    def _find_project_parent_location(self):
        StockLocation = self.env['stock.location']

        wh_location = StockLocation.search([
            ('name', '=', 'WH'),
            ('usage', '=', 'view')
        ], limit=1)

        if not wh_location:
            raise UserError("Warehouse (WH) parent location not found!")

        project_location = StockLocation.search([
            ('name', '=', 'Project Location'),
            ('usage', '=', 'internal'),
            ('location_id', '=', wh_location.id)
        ], limit=1)

        if not project_location:
            project_location = StockLocation.create({
                'name': 'Project Location',
                'usage': 'internal',
                'location_id': wh_location.id,
            })

        return project_location

    def _find_project_parent_location_of_root_bom(self,root_bom):
        project = self._find_project_parent_location()

        StockLocation = self.env['stock.location']

        name = root_bom.project_id.name
        project_location = StockLocation.search([
            ('name', '=', name),
            ('usage', '=', 'internal'),
            ('location_id', '=', project.id)
        ], limit=1)

        if not project_location:
            project_location = StockLocation.create({
                'name': name,
                'usage': 'internal',
                'location_id': project.id,
            })

        return project_location



    def _check_all_children_approved(self, bom_line):
        """
        Recursively check if all children (sub-BOMs) have approve_to_manufacture = True
        Only checks lines that have child BOMs
        """
        # Get child BOM using _bom_find which returns dict in Odoo 18
        bom_dict = self.env['mrp.bom']._bom_find(
            bom_line.product_id,
            bom_type='normal',
            company_id=self.company_id.id
        )

        # Extract actual bom record from dict
        if isinstance(bom_dict, dict):
            child_bom = bom_dict.get('bom', False)
        else:
            child_bom = bom_dict

        if not child_bom or not isinstance(child_bom, type(self)):
            # Leaf line (no child BOM) - always approved, no check needed
            return True

        # Has child BOM - check its approval and all its lines recursively
        if not bom_line.approve_to_manufacture:
            return False

        for child_line in child_bom.bom_line_ids:
            if not self._check_all_children_approved(child_line):
                return False

        return True

    def action_create_mo_from_overview(self):
        """
        Called from BOM overview Manufacture button
        """
        if self.is_evr:
            unapproved_lines = []

            for line in self.bom_line_ids:
                if not self._check_all_children_approved(line):
                    unapproved_lines.append(line.product_id.display_name)

            if unapproved_lines:
                raise ValidationError(
                    "Cannot create MO. The following BOM lines or their sub-components are not approved for manufacture:\n" +
                    "\n".join([f"- {name}" for name in unapproved_lines])
                )

        # Return action to create MO
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'name': 'Manufacture Orders',
            'views': [[False, 'form']],
            'target': 'current',
            'context': {'default_bom_id': self.id},
        }


    def _get_flattened_totals(self, product, quantity=1, bom_line=False):
        """Override to pass parent bom line context"""
        if bom_line and self.is_evr:
            return super(MrpBom, self.with_context(parent_bom_line_id=bom_line.id))._get_flattened_totals(product,
                                                                                                          quantity,
                                                                                                          bom_line)
        return super()._get_flattened_totals(product, quantity, bom_line)

    def _get_sub_boms(self, product, bom_line=False):
        """Stop recursion when EVR line is NOT approved."""
        # If EVR and bom_line exists and is not approved → DO NOT recurse
        if bom_line and self.is_evr and not bom_line.approve_to_manufacture:
            return []

        return super()._get_sub_boms(product, bom_line)

    def action_create_child_mos_recursive(self, root_bom=None, parent_mo=None, index="0", level=0, parent_qty=1.0,
                                          parent_branch_location=None):
        """
        Create MOs ONLY for BOM lines that have a child BOM.
        Each MO will have:
        1. Components: WH/Stock → Virtual/Production
        2. Finished Product: Virtual/Production → Own Branch Location → Parent Branch Location
        """
        Branch = self.env['mrp.bom.line.branch']

        if root_bom is None:
            root_bom = self
            if not hasattr(self.__class__, '_branch_assignment_cache'):
                self.__class__._branch_assignment_cache = {}

            cache_key = f"bom_{root_bom.id}"
            self.__class__._branch_assignment_cache[cache_key] = {
                'assignments': {},
                'seen_paths': []
            }

        created_mo = None
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        stock_location = warehouse.lot_stock_id if warehouse else False

        for line_idx, line in enumerate(self.bom_line_ids):
            if not line.child_bom_id:
                continue

            child_bom = line.child_bom_id
            child_qty = float(line.product_qty or 1.0) * parent_qty
            line_index = f"{index}{line_idx}"

            branches = Branch.search([
                ('bom_id', '=', root_bom.id),
                ('bom_line_id', '=', line.id)
            ], order='sequence')

            branch_rec = False
            if branches:
                if len(branches) == 1:
                    branch_rec = branches[0]
                else:
                    branch_rec = self._get_branch_for_mo_line(
                        branches=branches,
                        line=line,
                        index=line_index,
                        root_bom_id=root_bom.id
                    )

            current_branch_location = False
            branch_name = ""

            if branch_rec and branch_rec.location_id:
                current_branch_location = branch_rec.location_id.id
                branch_name = branch_rec.branch_name

            # Determine final destination (parent's branch location or project location)
            final_dest_location = parent_branch_location if parent_branch_location else root_bom.cfe_project_location_id.id

            mo_vals = {
                'product_id': child_bom.product_tmpl_id.product_variant_id.id,
                'product_uom_id': child_bom.product_uom_id.id,
                'product_qty': child_qty,
                'bom_id': child_bom.id,
                'root_bom_id': root_bom.id,
                'parent_mo_id': parent_mo.id if parent_mo else False,
                'project_id': root_bom.project_id.id,
                'line': line.id,
                'location_src_id': stock_location.id if stock_location else False,
                'location_dest_id': final_dest_location if final_dest_location else False,
                'state': 'draft',
            }

            # # Pass context for stock move customization
            # mo = self.env['mrp.production'].with_context(
            #     branch_intermediate_location=current_branch_location,
            #     branch_final_location=final_dest_location
            # ).create(mo_vals)

            # In action_create_child_mos_recursive method, add this context:

            mo = self.env['mrp.production'].with_context(
                branch_intermediate_location=current_branch_location,
                branch_final_location=final_dest_location,
                skip_component_moves=True  # Add this line
            ).create(mo_vals)

            created_mo = mo

            src_name = stock_location.display_name if stock_location else "WH/Stock"
            intermediate_name = self.env['stock.location'].browse(
                current_branch_location).display_name if current_branch_location else "N/A"
            final_name = self.env['stock.location'].browse(
                final_dest_location).display_name if final_dest_location else "N/A"


            self.env['bus.bus']._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {
                    "title": "Manufacturing Order Created",
                    "message": (
                        f"MO {mo.name} created for {child_bom.display_name}\n"
                        f"Branch: {branch_name}\n"
                        f"Quantity: {child_qty}\n"
                        f"Flow: {src_name} → {intermediate_name} → {final_name}"
                    ),
                    "sticky": False,
                    "type": "info",
                }
            )

            # Recurse: pass current branch location as parent for children
            child_bom.action_create_child_mos_recursive(
                root_bom=root_bom,
                parent_mo=mo,
                index=line_index,
                level=level + 1,
                parent_qty=child_qty,
                parent_branch_location=current_branch_location
            )

        if level == 0 and root_bom == self:
            cache_key = f"bom_{root_bom.id}"
            if hasattr(self.__class__, '_branch_assignment_cache'):
                if cache_key in self.__class__._branch_assignment_cache:
                    del self.__class__._branch_assignment_cache[cache_key]

        return created_mo

    def _get_branch_for_mo_line(self, branches, line, index, root_bom_id):
        """Determine which branch to use for this MO based on the traversal path."""
        cache_key = f"bom_{root_bom_id}"

        if not hasattr(self.__class__, '_branch_assignment_cache'):
            return branches[0]

        cache = self.__class__._branch_assignment_cache.get(cache_key)
        if not cache:
            return branches[0]

        path_key = f"{root_bom_id}_{line.id}_{index}"

        if path_key not in cache['seen_paths']:
            existing_count = len([p for p in cache['seen_paths']
                                  if p.startswith(f"{root_bom_id}_{line.id}_")])

            if existing_count < len(branches):
                branch = branches[existing_count]
            else:
                branch = branches[-1]

            cache['assignments'][path_key] = branch.id
            cache['seen_paths'].append(path_key)
        else:
            branch_id = cache['assignments'].get(path_key)
            branch = self.env['mrp.bom.line.branch'].browse(branch_id)

        return branch