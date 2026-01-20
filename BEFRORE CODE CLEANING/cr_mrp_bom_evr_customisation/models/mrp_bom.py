# cr_mrp_bom_customisation/models/mrp_bom.py
import string
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

    def create(self, vals_list):
        boms = super().create(vals_list)

        print("\n=== BOM CREATE HOOK START ===")
        for bom in boms:
            print(f"Processing BOM {bom.id} - {bom.display_name}")
            print(f"  is_evr: {bom.is_evr}")

            # Skip if not EVR
            if not bom.is_evr:
                print("  Skipped: is_evr is FALSE")
                continue

            # Check project
            project = bom.project_id
            print(f"  project_id: {project.id if project else None}")

            if not project:
                print("  Skipped: No project_id found")
                continue

            # parent: Project Location
            parent_loc = bom._find_project_parent_location()
            print(f"  parent Project Location found: {parent_loc.id} - {parent_loc.name}")

            loc_name = project.name
            print(f"  target new sublocation name = {loc_name}")

            Location = self.env['stock.location']

            # Check existing location
            existing = Location.search([
                ('name', '=', loc_name),
                ('location_id', '=', parent_loc.id),
                ('usage', '=', 'internal')
            ], limit=1)

            if existing:
                print(f"  Existing location FOUND: {existing.id} ({existing.name})")
                bom.cfe_project_location_id = existing.id
                continue

            print("  No existing location found → Creating new one...")

            # Create new location
            new_loc = Location.create({
                'name': loc_name,
                'location_id': parent_loc.id,
                'usage': 'internal',
            })

            print(f"  Created NEW location: {new_loc.id} - {new_loc.name}")

            # Assign to BOM
            bom.cfe_project_location_id = new_loc.id
            print(f"  Assigned location to BOM: {bom.cfe_project_location_id.id}")

        print("=== BOM CREATE HOOK END ===\n")

        # -----------------------------------------------------
        #  PART 2 — RECURSIVE MO CREATION
        # -----------------------------------------------------
        for bom in boms:
            if bom.is_evr:
                print(f"\n[DEBUG] Starting recursive MO creation for BOM {bom.display_name}")
                bom.action_create_child_mos_recursive()
                print(f"[DEBUG] Finished recursive MO creation for BOM {bom.display_name}")

        print("\n=== BOM CREATE HOOK END ===\n")

        return boms

    def write(self, vals):
        res = super().write(vals)

        print("\n=== BOM WRITE HOOK START ===")
        for bom in self:
            print(f"Processing BOM {bom.id} - {bom.display_name}")
            print(f"  is_evr: {bom.is_evr}")
            print(f"  vals: {vals}")

            # Only run if:
            # - is_evr becomes True
            # - OR project_id changed
            if not bom.is_evr:
                print("  Skipped: is_evr FALSE")
                continue

            if 'project_id' not in vals and 'is_evr' not in vals:
                print("  Skipped: irrelevant write")
                continue

            project = bom.project_id
            print(f"  project_id: {project.id if project else None}")

            if not project:
                print("  Skipped: no project assigned")
                continue

            parent_loc = bom._find_project_parent_location()
            print(f"  parent Project Location found: {parent_loc.id} - {parent_loc.name}")

            loc_name = project.name
            print(f"  target sublocation name = {loc_name}")

            Location = self.env['stock.location']

            # Find existing
            existing = Location.search([
                ('name', '=', loc_name),
                ('location_id', '=', parent_loc.id),
                ('usage', '=', 'internal')
            ], limit=1)

            if existing:
                print(f"  Existing location FOUND: {existing.id} ({existing.name})")
                bom.cfe_project_location_id = existing.id
                continue

            print("  No existing location found → Creating new one...")

            new_loc = Location.create({
                'name': loc_name,
                'location_id': parent_loc.id,
                'usage': 'internal',
            })

            print(f"  Created NEW location: {new_loc.id} - {new_loc.name}")

            bom.cfe_project_location_id = new_loc.id
            print(f"  Assigned location to BOM: {bom.cfe_project_location_id.id}")

        print("=== BOM WRITE HOOK END ===\n")
        return res

    def _assign_branches_for_bom(self):
        """
        Assign branch codes for each root BOM in `self`.
        Uses path-based unique branch creation and ALSO creates stock.locations
        same as old code.
        """

        print("\n========================")
        print(f"🔥 ENTERED _assign_branches_for_bom FOR BOM {self.id}")
        print("========================\n")

        Branch = self.env['mrp.bom.line.branch']
        codes = _generate_branch_codes()

        for root_bom in self:

            if self.env.context.get('skip_branch_recompute'):
                continue

            print(f"\n=== START assigning branches for root BOM {root_bom.id} ({root_bom.display_name}) ===")

            # remove previous mappings for this root
            old = Branch.search([('bom_id', '=', root_bom.id)])
            if old:
                print(f"Removing {len(old)} existing branch mappings for BOM {root_bom.id}")
                old.unlink()

            idx = 0  # start assigning from A

            # DFS
            def dfs(current_bom):
                nonlocal idx

                lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))
                print(f"DFS entering BOM {current_bom.id} with {len(lines)} lines")

                for line in lines:

                    if line.child_bom_id:

                        if idx >= len(codes):
                            raise UserError("No more branch codes available.")

                        code = codes[idx]
                        idx += 1

                        # UNIQUE ID for this occurrence
                        path_uid = uuid.uuid4().hex

                        # 📌 LOCATION CREATION ADDED HERE (same as old code)
                        project_parent = self._find_project_parent_location()
                        loc = self.env['stock.location'].create({
                            'name': code,  # OR f"{root_bom.display_name}-{code}"
                            'location_id': project_parent.id,
                            'usage': 'internal',
                        })

                        # 📌 CREATE branch mapping WITH LOCATION
                        Branch.create({
                            'bom_id': root_bom.id,
                            'bom_line_id': line.id,
                            'branch_name': code,
                            'sequence': idx,
                            'path_uid': path_uid,
                            'location_id': loc.id,  # <--- 🔥 THIS WAS MISSING IN YOUR NEW CODE
                        })

                        print(f"  CREATE mapping line={line.id} -> {code} (loc={loc.id}) path={path_uid}")

                        # now go deeper
                        dfs(line.child_bom_id)

                    else:
                        print(f"  Leaf line {line.id} → no mapping")

            dfs(root_bom)

            total_assigned = Branch.search_count([('bom_id', '=', root_bom.id)])
            print(f"=== DONE assigning branches for root BOM {root_bom.id}. total_assigned={total_assigned} ===\n")

        return True

    def _dfs_assign(self, root_bom, bom, branch_letter, path_uid):
        """Recursive DFS that assigns one branch letter per path."""
        _logger.info(f"DFS entering BOM {bom.id} ({bom.display_name}) path={path_uid} branch={branch_letter}")

        for line in bom.bom_line_ids:

            # Create new mapping for every path
            self.env["mrp.bom.line.branch"].create({
                'bom_id': root_bom.id,
                'bom_line_id': line.id,
                'branch_name': branch_letter,
                'sequence': line.sequence,
                'path_uid': path_uid,
            })

            _logger.info(
                f"  MAPPING: root={root_bom.display_name} | line={line.id} | "
                f"branch={branch_letter} | product={line.product_id.display_name} | path={path_uid}"
            )

            # Go deeper if child BOM exists
            if line.child_bom_id:
                self._dfs_assign(
                    root_bom=root_bom,
                    bom=line.child_bom_id,
                    branch_letter=branch_letter,
                    path_uid=path_uid,
                )

    def action_assign_branches(self):
        for bom in self:
            bom._assign_branches_for_bom()
        return True

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

        if bom_line:
            print(
                f"[SUB-BOM CHECK] bom_line {bom_line.id} | product {bom_line.product_id.id} | approved={bom_line.approve_to_manufacture}")

        # If EVR and bom_line exists and is not approved → DO NOT recurse
        if bom_line and self.is_evr and not bom_line.approve_to_manufacture:
            print(f"[SUB-BOM BLOCKED] SKIP recursion for bom_line {bom_line.id}")
            return []

        print("[SUB-BOM OK] Recursing normally")
        return super()._get_sub_boms(product, bom_line)



    # def action_create_child_mos_recursive(self, root_bom=None, parent_mo=None, index="0", level=0, parent_qty=1.0):
    #     """
    #     Create MOs ONLY for BOM lines that have a child BOM.
    #     DO NOT create an MO for the main BOM.
    #     """
    #     Branch = self.env['mrp.bom.line.branch']
    #
    #     if root_bom is None:
    #         root_bom = self
    #         if not hasattr(self.__class__, '_branch_assignment_cache'):
    #             self.__class__._branch_assignment_cache = {}
    #
    #         cache_key = f"bom_{root_bom.id}"
    #         self.__class__._branch_assignment_cache[cache_key] = {
    #             'assignments': {},
    #             'seen_paths': []
    #         }
    #
    #     created_mo = None
    #
    #     for line_idx, line in enumerate(self.bom_line_ids):
    #         if not line.child_bom_id:
    #             continue
    #
    #         child_bom = line.child_bom_id
    #         child_qty = float(line.product_qty or 1.0) * parent_qty
    #         line_index = f"{index}{line_idx}"
    #
    #         dest_location = False
    #         dest_location_name = "Default"
    #         branch_name = ""
    #
    #         branches = Branch.search([
    #             ('bom_id', '=', root_bom.id),
    #             ('bom_line_id', '=', line.id)
    #         ], order='sequence')
    #
    #         branch_rec = False
    #         if branches:
    #             if len(branches) == 1:
    #                 branch_rec = branches[0]
    #             else:
    #                 branch_rec = self._get_branch_for_mo_line(
    #                     branches=branches,
    #                     line=line,
    #                     index=line_index,
    #                     root_bom_id=root_bom.id
    #                 )
    #
    #         if branch_rec:
    #             branch_name = branch_rec.branch_name
    #             if branch_rec.location_id:
    #                 dest_location = branch_rec.location_id.id
    #                 dest_location_name = branch_rec.location_id.display_name
    #
    #         mo_vals = {
    #             'product_id': child_bom.product_tmpl_id.product_variant_id.id,
    #             'product_uom_id': child_bom.product_uom_id.id,
    #             'product_qty': child_qty,
    #             'bom_id': child_bom.id,
    #             'root_bom_id': root_bom.id,
    #             'parent_mo_id': parent_mo.id if parent_mo else False,
    #             'project_id': root_bom.project_id.id,
    #             'line': line.id,
    #         }
    #
    #         if dest_location:
    #             mo_vals['location_dest_id'] = dest_location
    #
    #         mo = self.env['mrp.production'].with_context(branch_dest_location=dest_location).create(mo_vals)
    #         created_mo = mo
    #
    #         print(f"[DEBUG] >>> Created MO {mo.name}")
    #         print(f"[DEBUG]      Branch: {branch_name if branch_name else 'None'}")
    #         print(f"[DEBUG]      Quantity: {child_qty}")
    #         print(f"[DEBUG]      dest = {dest_location_name}")
    #
    #         self.env['bus.bus']._sendone(
    #             self.env.user.partner_id,
    #             "simple_notification",
    #             {
    #                 "title": "Manufacturing Order Created",
    #                 "message": (
    #                     f"MO {mo.name} created for {child_bom.display_name}\n"
    #                     f"Branch: {branch_name if branch_name else 'N/A'}\n"
    #                     f"Quantity: {child_qty}\n"
    #                     f"Destination: {dest_location_name}"
    #                 ),
    #                 "sticky": False,
    #                 "type": "info",
    #             }
    #         )
    #
    #         child_bom.action_create_child_mos_recursive(
    #             root_bom=root_bom,
    #             parent_mo=mo,
    #             index=line_index,
    #             level=level + 1,
    #             parent_qty=child_qty
    #         )
    #
    #     if level == 0 and root_bom == self:
    #         cache_key = f"bom_{root_bom.id}"
    #         if hasattr(self.__class__, '_branch_assignment_cache'):
    #             if cache_key in self.__class__._branch_assignment_cache:
    #                 del self.__class__._branch_assignment_cache[cache_key]
    #
    #     return created_mo


    # def _get_branch_for_mo_line(self, branches, line, index, root_bom_id):
    #     """Determine which branch to use for this MO based on the traversal path."""
    #     cache_key = f"bom_{root_bom_id}"
    #
    #     if not hasattr(self.__class__, '_branch_assignment_cache'):
    #         return branches[0]
    #
    #     cache = self.__class__._branch_assignment_cache.get(cache_key)
    #     if not cache:
    #         return branches[0]
    #
    #     path_key = f"{root_bom_id}_{line.id}_{index}"
    #
    #     if path_key not in cache['seen_paths']:
    #         existing_count = len([p for p in cache['seen_paths']
    #                               if p.startswith(f"{root_bom_id}_{line.id}_")])
    #
    #         if existing_count < len(branches):
    #             branch = branches[existing_count]
    #         else:
    #             branch = branches[-1]
    #
    #         cache['assignments'][path_key] = branch.id
    #         cache['seen_paths'].append(path_key)
    #     else:
    #         branch_id = cache['assignments'].get(path_key)
    #         branch = self.env['mrp.bom.line.branch'].browse(branch_id)
    #
    #     return branch

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
            }

            # Pass context for stock move customization
            mo = self.env['mrp.production'].with_context(
                branch_intermediate_location=current_branch_location,
                branch_final_location=final_dest_location
            ).create(mo_vals)

            created_mo = mo

            src_name = stock_location.display_name if stock_location else "WH/Stock"
            intermediate_name = self.env['stock.location'].browse(
                current_branch_location).display_name if current_branch_location else "N/A"
            final_name = self.env['stock.location'].browse(
                final_dest_location).display_name if final_dest_location else "N/A"

            print(f"[DEBUG] >>> Created MO {mo.name}")
            print(f"[DEBUG]      Branch: {branch_name}")
            print(f"[DEBUG]      Quantity: {child_qty}")
            print(f"[DEBUG]      Flow: {src_name} → {intermediate_name} → {final_name}")

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