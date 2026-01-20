# cr_mrp_bom_customisation/models/mrp_bom.py
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

    def _assign_branches_for_bom(self, root_bom):
        """
        Definitive DFS assignment:
         - assign a code to a *line* only if that line has child_bom_id
         - assign code BEFORE recursing into child BOM
         - use single idx across entire traversal for this root_bom
         - store results in mrp.bom.line.branch (bom_id = root_bom.id)
        """
        self.ensure_one()
        Branch = self.env['mrp.bom.line.branch']
        codes = _generate_branch_codes()
        idx = 0

        _logger.info("=== START assigning branches for root BOM %s (%s) ===", root_bom.id, root_bom.display_name)
        print(f"\n=== START assigning branches for root BOM {root_bom.id} ({root_bom.display_name}) ===")

        # remove previous mappings for this root
        old = Branch.search([('bom_id', '=', root_bom.id)])
        if old:
            print(f"Removing {len(old)} existing branch mappings for BOM {root_bom.id}")
            old.unlink()

        # explicit recursive DFS - assign to parent line that has child_bom
        def dfs(current_bom):
            nonlocal idx
            # deterministic ordering
            lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))
            print(f"DFS entering BOM {current_bom.id} (root {root_bom.id}) with {len(lines)} lines")
            _logger.debug("DFS entering BOM %s (root %s) with %s lines", current_bom.id, root_bom.id, len(lines))

            for line in lines:
                # check if this line has a sub-bom
                child_bom = line.child_bom_id
                # DEBUG: show line context
                print(f"  Inspect line {line.id} product={getattr(line.product_id, 'display_name', False)} child_bom_id={getattr(child_bom, 'id', False)}")
                _logger.debug("Inspect line %s product=%s child_bom=%s", line.id, getattr(line.product_id, 'display_name', ''), getattr(child_bom, 'id', False))

                if child_bom:
                    # assign next code to THIS LINE (the parent)
                    if idx >= len(codes):
                        raise UserWarning(_("No more branch codes available for this BOM."))

                    code = codes[idx]
                    idx += 1

                    # create or update mapping for (root_bom, line)
                    existing = Branch.search([('bom_id', '=', root_bom.id), ('bom_line_id', '=', line.id)], limit=1)
                    if existing:
                        if existing.branch_name != code:
                            print(f"  UPDATE mapping root_bom={root_bom.id} line={line.id} -> {code}")
                            existing.write({'branch_name': code, 'sequence': idx})
                            _logger.info("Updated branch mapping root %s line %s -> %s", root_bom.id, line.id, code)
                    else:
                        print(f"  CREATE mapping root_bom={root_bom.id} line={line.id} -> {code}")
                        # Branch.create({
                        #     'bom_id': root_bom.id,
                        #     'bom_line_id': line.id,
                        #     'branch_name': code,
                        #     'sequence': idx,
                        # })
                        project_parent = self._find_project_parent_location()

                        # branch location name
                        # loc_name = f"{root_bom.display_name} - {code}"
                        loc_name = f"{code}"

                        loc = self.env['stock.location'].create({
                            'name': loc_name,
                            'location_id': project_parent.id,
                            'usage': 'internal',
                        })

                        mapping = Branch.create({
                            'bom_id': root_bom.id,
                            'bom_line_id': line.id,
                            'branch_name': code,
                            'sequence': idx,
                            'location_id': loc.id,  # 🔥 assign location
                        })

                        _logger.info("Created branch mapping root %s line %s -> %s", root_bom.id, line.id, code)

                    # Important: assign BEFORE recursion so parent gets code
                    # then recurse to child's BOM
                    dfs(child_bom)

                else:
                    # ensure no stale mapping for leaf under this root
                    existing = Branch.search([('bom_id', '=', root_bom.id), ('bom_line_id', '=', line.id)], limit=1)
                    if existing:
                        print(f"  REMOVING stale mapping for root {root_bom.id} line {line.id} (leaf)")
                        existing.unlink()
                        _logger.info("Removed stale mapping for root %s line %s", root_bom.id, line.id)

            # end for

        # run dfs from root_bom
        dfs(root_bom)

        total_assigned = Branch.search_count([('bom_id', '=', root_bom.id)])
        _logger.info("=== DONE assigning branches for root BOM %s. total_assigned=%s ===", root_bom.id, total_assigned)
        print(f"=== DONE assigning branches for root BOM {root_bom.id}. total_assigned={total_assigned} ===\n")
        return True

    def action_assign_branches(self):
        for bom in self:
            bom._assign_branches_for_bom(bom)
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


    # def explode(self, product, quantity, picking_type=False, never_attribute_values=False):
    #     """
    #     Override explode to filter out non-approved BOM lines
    #     """
    #
    #     if not self.is_evr:
    #         return super().explode(product, quantity, picking_type, never_attribute_values)
    #
    #     # First explosion
    #     boms_done, lines_done = super().explode(
    #         product, quantity, picking_type, never_attribute_values
    #     )
    #
    #     filtered_lines = []
    #
    #     for bom_line, line_data in lines_done:
    #         # Check if this line has a child BOM
    #         bom_dict = self.env['mrp.bom']._bom_find(
    #             bom_line.product_id,
    #             bom_type='normal',
    #             company_id=self.company_id.id
    #         )
    #
    #         # Check if dictionary has any BOM entries
    #         has_child_bom = False
    #         if isinstance(bom_dict, dict) and len(bom_dict) > 0:
    #             # Get the first BOM from dictionary
    #             child_bom = next(iter(bom_dict.values()), False)
    #             if child_bom and isinstance(child_bom, type(self)):
    #                 has_child_bom = True
    #
    #         # If has child BOM and not approved, skip this line and all its children
    #         if has_child_bom and not bom_line.approve_to_manufacture:
    #             continue
    #
    #         # Include this line
    #         filtered_lines.append((bom_line, line_data))
    #
    #     return boms_done, filtered_lines

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

    # def explode(self, product, quantity, picking_type=False, never_attribute_values=None):
    #     print(f"\n========== ENTER explode() for BOM {self.id} ==========")
    #     print(f"Product: {product.id} | Qty: {quantity} | is_evr={self.is_evr}")
    #
    #     boms_done, lines_done = super().explode(
    #         product, quantity, picking_type, never_attribute_values
    #     )
    #
    #     print(f"super().explode returned -> {len(boms_done)} boms, {len(lines_done)} lines")
    #
    #     # If not EVR → no filtering
    #     if not self.is_evr:
    #         print("EVR disabled → returning results unchanged")
    #         return boms_done, lines_done
    #
    #     filtered_lines = []
    #
    #     for bom_line, line_data in lines_done:
    #         print("------------------------------------------------------------")
    #         print(f"Line {bom_line.id} | product {bom_line.product_id.id} | approved={bom_line.approve_to_manufacture}")
    #
    #         # Detect child BOM (only for information, recursion is controlled elsewhere)
    #         bom_dict = self.env['mrp.bom']._bom_find(
    #             bom_line.product_id,
    #             bom_type='normal',
    #             company_id=self.company_id.id
    #         )
    #
    #         print(f"_bom_find returned: {bom_dict}")
    #
    #         child_bom = None
    #         if isinstance(bom_dict, dict) and bom_dict:
    #             maybe = next(iter(bom_dict.values()))
    #             if isinstance(maybe, type(self)):
    #                 child_bom = maybe
    #                 print(f"Child BOM detected: {child_bom.id}")
    #
    #         # SKIP if unapproved AND child BOM exists
    #         if child_bom and not bom_line.approve_to_manufacture:
    #             print(f">>> SKIPPING line {bom_line.id}: has child BOM {child_bom.id} and is NOT approved")
    #             continue
    #
    #         print(f"Including line {bom_line.id}")
    #         filtered_lines.append((bom_line, line_data))
    #
    #     print(f"Final lines after filtering: {len(filtered_lines)}")
    #     print(f"========== EXIT explode() for BOM {self.id} ==========\n")
    #
    #     return boms_done, filtered_lines


    def explode(self, product, quantity, picking_type=False, never_attribute_values=None):
        print(f"\n========== ENTER explode() for BOM {self.id} ==========")
        print(f"Product: {product.id} | Qty: {quantity} | is_evr={self.is_evr}")

        boms_done, lines_done = super().explode(
            product, quantity, picking_type, never_attribute_values
        )

        print(f"super().explode returned -> {len(boms_done)} boms, {len(lines_done)} lines")

        if not self.is_evr:
            print("EVR disabled → returning results unchanged")
            return boms_done, lines_done

        filtered_lines = []

        for bom_line, line_data in lines_done:
            print("------------------------------------------------------------")
            print(f"Line {bom_line.id} | product {bom_line.product_id.id} | approved={bom_line.approve_to_manufacture}")

            # Check entire nested BOM tree
            current_product = bom_line.product_id
            has_unapproved_child = False
            checked_boms = set()
            boms_to_check = []

            # Find initial child BOM
            bom_dict = self.env['mrp.bom']._bom_find(
                current_product,
                bom_type='normal',
                company_id=self.company_id.id
            )

            print(f"_bom_find returned: {bom_dict}")

            if isinstance(bom_dict, dict) and bom_dict:
                maybe = next(iter(bom_dict.values()), None)
                if maybe and isinstance(maybe, type(self)):
                    boms_to_check.append((bom_line, maybe))

            # While loop to check all nested BOMs
            while boms_to_check:
                current_bom_line, current_bom = boms_to_check.pop(0)

                if current_bom.id in checked_boms:
                    continue

                checked_boms.add(current_bom.id)
                print(
                    f"  Checking nested BOM {current_bom.id} | Line {current_bom_line.id} approved={current_bom_line.approve_to_manufacture}")

                # If this level is not approved, mark as unapproved
                if not current_bom_line.approve_to_manufacture:
                    print(f"  >>> Found unapproved line {current_bom_line.id} at BOM {current_bom.id}")
                    has_unapproved_child = True
                    break

                # Add all child lines of this BOM to check queue
                for nested_line in current_bom.bom_line_ids:
                    nested_bom_dict = self.env['mrp.bom']._bom_find(
                        nested_line.product_id,
                        bom_type='normal',
                        company_id=self.company_id.id
                    )

                    if isinstance(nested_bom_dict, dict) and nested_bom_dict:
                        nested_maybe = next(iter(nested_bom_dict.values()), None)
                        if nested_maybe and isinstance(nested_maybe, type(self)):
                            boms_to_check.append((nested_line, nested_maybe))

            # SKIP if any nested BOM has unapproved line
            if has_unapproved_child:
                print(f">>> SKIPPING line {bom_line.id}: has unapproved nested BOM")
                continue

            print(f"Including line {bom_line.id}")
            filtered_lines.append((bom_line, line_data))

        print(f"Final lines after filtering: {len(filtered_lines)}")
        print(f"========== EXIT explode() for BOM {self.id} ==========\n")
        return boms_done, filtered_lines

    # def action_create_child_mos_recursive(self, root_bom=None, parent_mo=None):
    #     """
    #     Recursively create MOs for BOMs.
    #     Destination location is determined from branch location of the parent line.
    #     """
    #     Branch = self.env['mrp.bom.line.branch']
    #
    #     if root_bom is None:
    #         root_bom = self
    #
    #     # --------------------------------------------------------
    #     # 1. Determine destination location for THIS BOM's MO
    #     # --------------------------------------------------------
    #     dest_location = False
    #
    #     if parent_mo:
    #         # Find the parent bom line that points to this BOM
    #         parent_line = self.env['mrp.bom.line'].search([
    #             ('child_bom_id', '=', self.id)
    #         ], limit=1)
    #
    #         if parent_line:
    #             # find branch mapping
    #             branch_rec = Branch.search([
    #                 ('bom_id', '=', root_bom.id),
    #                 ('bom_line_id', '=', parent_line.id)
    #             ], limit=1)
    #
    #             if branch_rec:
    #                 dest_location = branch_rec.location_id.id
    #
    #     # --------------------------------------------------------
    #     # 2. Create MO for this BOM
    #     # --------------------------------------------------------
    #     mo_vals = {
    #         'product_id': self.product_id.id,
    #         'product_uom_id': self.product_uom_id.id,
    #         'product_qty': 1,
    #         'bom_id': self.id,
    #         'root_bom_id': root_bom.id,
    #         'parent_mo_id': parent_mo.id if parent_mo else False,
    #     }
    #
    #     # assign destination location
    #     if dest_location:
    #         mo_vals['location_dest_id'] = dest_location
    #
    #     mo = self.env['mrp.production'].create(mo_vals)
    #
    #     print(f"[DEBUG] Created MO {mo.name} for BOM {self.display_name} dest={dest_location}")
    #
    #     # --------------------------------------------------------
    #     # 3. Recursively create child MOs
    #     # --------------------------------------------------------
    #     for line in self.bom_line_ids:
    #         if line.child_bom_id:
    #             print(f"[DEBUG] Found child BOM {line.child_bom_id.display_name} under {self.display_name}")
    #
    #             line.child_bom_id.action_create_child_mos_recursive(
    #                 root_bom=root_bom,
    #                 parent_mo=mo
    #             )
    #
    #     return mo

    def action_create_child_mos_recursive(self, root_bom=None, parent_mo=None):
        """
        Create MOs ONLY for BOM lines that have a child BOM.
        DO NOT create an MO for the main BOM.
        """
        Branch = self.env['mrp.bom.line.branch']

        if root_bom is None:
            root_bom = self

        created_mo = None  # default

        # --------------------------------------------------------
        # LOOP THROUGH ALL BOM LINES
        # --------------------------------------------------------
        for line in self.bom_line_ids:

            if not line.child_bom_id:
                print(f"[DEBUG] No child BOM for line {line.id} → SKIP")
                continue

            child_bom = line.child_bom_id
            print(f"[DEBUG] Creating MO for child BOM {child_bom.display_name}")

            # --------------------------------------------------------
            # Determine destination location based on THIS line
            # --------------------------------------------------------
            dest_location = False
            dest_location_name = "Default"

            branch_rec = Branch.search([
                ('bom_id', '=', root_bom.id),
                ('bom_line_id', '=', line.id)
            ], limit=1)

            if branch_rec:
                dest_location = branch_rec.location_id.id
                dest_location_name = branch_rec.location_id.display_name

            # --------------------------------------------------------
            # Create MO for the child BOM
            # --------------------------------------------------------
            mo_vals = {
                'product_id': child_bom.product_tmpl_id.product_variant_id.id,
                'product_uom_id': child_bom.product_uom_id.id,
                'product_qty': 1,
                'bom_id': child_bom.id,
                'root_bom_id': root_bom.id,
                'parent_mo_id': parent_mo.id if parent_mo else False,
                'project_id':root_bom.project_id.id,
                'line': line.id,
            }

            if dest_location:
                mo_vals['location_dest_id'] = dest_location

            mo = self.env['mrp.production'].create(mo_vals)
            created_mo = mo

            print(f"[DEBUG] >>> Created MO {mo.name} for BOM {child_bom.display_name}")
            print(f"[DEBUG]      dest = {dest_location_name}")

            # Send notification
            # Send Web Notification (Odoo bus)
            self.env['bus.bus']._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {
                    "title": "Manufacturing Order Created",
                    "message": (
                        f"MO {mo.name} created for {child_bom.display_name}\n"
                        f"Destination: {dest_location_name}"
                    ),
                    "sticky": False,
                    "type": "info",
                }
            )

            # --------------------------------------------------------
            # RECURSE: process THIS child BOM's own child lines
            # --------------------------------------------------------
            child_bom.action_create_child_mos_recursive(
                root_bom=root_bom,
                parent_mo=mo
            )

        return created_mo




