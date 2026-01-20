from odoo import api, SUPERUSER_ID, _
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
# cr_mrp_bom_customisation/hooks.py  (or models/mrp_bom.py if you prefer)
from odoo import api, SUPERUSER_ID, _
import logging

_logger = logging.getLogger(__name__)



def _generate_branch_codes():
    """A robust list of branch codes: A..Z, A1..A9, AA..ZZ"""
    codes = []
    # A..Z
    for c in range(ord('A'), ord('Z') + 1):
        codes.append(chr(c))
    # A1..A9 ... Z1..Z9
    for c in range(ord('A'), ord('Z') + 1):
        for d in range(1, 10):
            codes.append(f"{chr(c)}{d}")
    # AA..ZZ
    for c1 in range(ord('A'), ord('Z') + 1):
        for c2 in range(ord('A'), ord('Z') + 1):
            codes.append(chr(c1) + chr(c2))
    return codes


# def assign_branches_after_install(env):
#     """
#     Post-init hook entry. `env` here is an Environment (manifest must reference this hook name).
#     """
#     Bom = env["mrp.bom"]
#     BranchModel = env["mrp.bom.line.branch"]
#     Location = env["stock.location"]
#
#     _logger.info("=== assign_branches_after_install START ===")
#     all_boms = Bom.search([])
#     _logger.info("Total BOMs found: %s", len(all_boms))
#
#     codes = _generate_branch_codes()
#
#     for root_bom in all_boms:
#         _logger.info("Processing BOM %s - %s", root_bom.id, root_bom.display_name)
#         try:
#             # remove old mappings for this root BOM (optional)
#             old = BranchModel.search([("bom_id", "=", root_bom.id)])
#             if old:
#                 _logger.info("Removing %s existing branch mappings for BOM %s", len(old), root_bom.id)
#                 old.unlink()
#
#             # index into codes list
#             idx = 0
#
#             # depth-first assign
#             def _assign(current_bom):
#                 nonlocal idx
#                 # deterministic order
#                 lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))
#                 for line in lines:
#                     # assign only if line has a child BOM (i.e., this line points to a sub-BOM)
#                     child = line.child_bom_id
#                     if not child:
#                         # leaf line -> no branch mapping for this root_bom; skip
#                         continue
#
#                     # get next code
#                     if idx >= len(codes):
#                         raise UserWarning(_("No more branch codes available for BOM %s") % root_bom.display_name)
#                     code = codes[idx]
#                     idx += 1
#
#                     # create or update branch mapping for (root_bom, line)
#                     mapping = BranchModel.search([("bom_id", "=", root_bom.id),
#                                                   ("bom_line_id", "=", line.id)], limit=1)
#                     if mapping:
#                         if mapping.branch_name != code:
#                             _logger.info("Updating mapping for BOM %s line %s: %s -> %s",
#                                          root_bom.id, line.id, mapping.branch_name, code)
#                             mapping.write({'branch_name': code, 'sequence': idx})
#                     else:
#                         _logger.info("Creating mapping for BOM %s line %s -> %s", root_bom.id, line.id, code)
#                         # prepare mapping vals, create mapping after creating/locating location
#                         mapping = BranchModel.create({
#                             'bom_id': root_bom.id,
#                             'bom_line_id': line.id,
#                             'branch_name': code,
#                             'sequence': idx,
#                         })
#
#                     # create or reuse location for this branch under project parent
#                     try:
#                         parent = _find_project_parent_location(env)
#                         loc_name = f"{root_bom.display_name or root_bom.product_tmpl_id.name} - {code}"
#                         # loc_name = f"{code}"
#                         existing_loc = Location.search([('name', '=', loc_name), ('location_id', '=', parent.id)], limit=1) if parent else Location.search([('name','=',loc_name)], limit=1)
#                         if existing_loc:
#                             loc = existing_loc
#                         else:
#                             loc = Location.create({
#                                 'name': loc_name,
#                                 'location_id': parent.id if parent else False,
#                                 'usage': 'internal',
#                             })
#                             _logger.info("Created branch location %s (parent %s)", loc.name, parent.name if parent else None)
#                         # attach to mapping
#                         if loc and mapping and mapping.location_id.id != loc.id:
#                             mapping.location_id = loc.id
#                     except Exception as e:
#                         _logger.exception("Failed to create/attach branch location for BOM %s branch %s: %s", root_bom.id, code, e)
#
#                     # recurse into the child BOM (continue same idx sequence)
#                     _assign(child)
#
#             # run assign for this root
#             _assign(root_bom)
#
#             total = BranchModel.search_count([("bom_id", "=", root_bom.id)])
#             _logger.info("Completed BOM %s - Created/Updated %s branch mappings", root_bom.id, total)
#
#         except Exception as e:
#             # do not fail entire run; log and continue
#             _logger.exception("Error processing BOM %s: %s", root_bom.id, e)
#
#     _logger.info("=== assign_branches_after_install END ===")


def post_init_hook(env):
    assign_branches_after_install(env)


def assign_branches_after_install(env):
    """
    Post-init hook entry. `env` here is an Environment (manifest must reference this hook name).
    """
    Bom = env["mrp.bom"]
    BranchModel = env["mrp.bom.line.branch"]
    Location = env["stock.location"]

    _logger.info("=== assign_branches_after_install START ===")
    all_boms = Bom.search([])
    _logger.info("Total BOMs found: %s", len(all_boms))

    codes = _generate_branch_codes()

    for root_bom in all_boms:
        _logger.info("Processing BOM %s - %s", root_bom.id, root_bom.display_name)
        try:
            # remove old mappings for this root BOM (optional)
            old = BranchModel.search([("bom_id", "=", root_bom.id)])
            if old:
                _logger.info("Removing %s existing branch mappings for BOM %s", len(old), root_bom.id)
                old.unlink()

            # index into codes list
            idx = 0

            # depth-first assign
            def _assign(current_bom):
                nonlocal idx
                # deterministic order
                lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))
                for line in lines:
                    # assign only if line has a child BOM (i.e., this line points to a sub-BOM)
                    child = line.child_bom_id
                    if not child:
                        # leaf line -> no branch mapping for this root_bom; skip
                        continue

                    # get next code
                    if idx >= len(codes):
                        raise UserWarning(_("No more branch codes available for BOM %s") % root_bom.display_name)
                    code = codes[idx]
                    idx += 1

                    # create or update branch mapping for (root_bom, line)
                    mapping = BranchModel.search([("bom_id", "=", root_bom.id),
                                                  ("bom_line_id", "=", line.id)], limit=1)
                    if mapping:
                        if mapping.branch_name != code:
                            _logger.info("Updating mapping for BOM %s line %s: %s -> %s",
                                         root_bom.id, line.id, mapping.branch_name, code)
                            mapping.write({'branch_name': code, 'sequence': idx})
                    else:
                        _logger.info("Creating mapping for BOM %s line %s -> %s", root_bom.id, line.id, code)
                        # prepare mapping vals, create mapping after creating/locating location
                        mapping = BranchModel.create({
                            'bom_id': root_bom.id,
                            'bom_line_id': line.id,
                            'branch_name': code,
                            'sequence': idx,
                        })

                    # create or reuse location for this branch under project parent
                    try:
                        parent = _find_project_parent_location(env)
                        # loc_name = f"{root_bom.display_name or root_bom.product_tmpl_id.name} - {code}"
                        loc_name = f"{code}"
                        existing_loc = Location.search([('name', '=', loc_name), ('location_id', '=', parent.id)], limit=1) if parent else Location.search([('name','=',loc_name)], limit=1)
                        # if existing_loc:
                        #     loc = existing_loc
                        # else:
                        #     loc = Location.create({
                        #         'name': loc_name,
                        #         'location_id': parent.id if parent else False,
                        #         'usage': 'internal',
                        #     })
                        #     _logger.info("Created branch location %s (parent %s)", loc.name, parent.name if parent else None)

                        loc = Location.create({
                            'name': loc_name,
                            'location_id': parent.id if parent else False,
                            'usage': 'internal',
                        })

                        _logger.info("Created branch location %s (parent %s)", loc.name,
                                     parent.name if parent else None)

                        # attach to mapping
                        if loc and mapping and mapping.location_id.id != loc.id:
                            mapping.location_id = loc.id
                    except Exception as e:
                        _logger.exception("Failed to create/attach branch location for BOM %s branch %s: %s", root_bom.id, code, e)

                    # recurse into the child BOM (continue same idx sequence)
                    _assign(child)

            # run assign for this root
            _assign(root_bom)

            total = BranchModel.search_count([("bom_id", "=", root_bom.id)])
            _logger.info("Completed BOM %s - Created/Updated %s branch mappings", root_bom.id, total)

        except Exception as e:
            # do not fail entire run; log and continue
            _logger.exception("Error processing BOM %s: %s", root_bom.id, e)

    _logger.info("=== assign_branches_after_install END ===")


# # helper to find project parent (simple heuristic; adapt to your system)
# def _find_project_parent_location(env):
#     StockLocation = env['stock.location']
#     # if you have 'location_category' selection like earlier, prefer it
#     parent = StockLocation.search([('location_category', '=', 'project')], limit=1)
#     if parent:
#         return parent
#     parent = StockLocation.search([('name', 'ilike', 'project')], limit=1)
#     if parent:
#         return parent
#     try:
#         return StockLocation.browse(env.ref('stock.stock_location_stock').id)
#     except Exception:
#         return StockLocation.search([('usage', '=', 'internal')], limit=1)

def _find_project_parent_location(env):
    StockLocation = env['stock.location']

    # Find WH stock location (parent)
    wh_location = StockLocation.search([
        ('name', '=', 'WH'),
        ('usage', '=', 'view')
    ], limit=1)

    if not wh_location:
        raise UserError("Warehouse (WH) parent location not found!")

    # Find existing 'Project Location'
    project_location = StockLocation.search([
        ('name', '=', 'Project Location'),
        ('usage', '=', 'internal'),
        ('location_id', '=', wh_location.id)
    ], limit=1)

    # If not found → create
    if not project_location:
        project_location = StockLocation.create({
            'name': 'Project Location',
            'usage': 'internal',
            'location_id': wh_location.id,
        })

    return project_location

