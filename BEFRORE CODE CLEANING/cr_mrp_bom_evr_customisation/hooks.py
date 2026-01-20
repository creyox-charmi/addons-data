from odoo import api, SUPERUSER_ID, _
import logging

from odoo.exceptions import UserError

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
            # remove old mappings for this root BOM
            old = BranchModel.search([("bom_id", "=", root_bom.id)])
            if old:
                _logger.info("Removing %s existing branch mappings for BOM %s", len(old), root_bom.id)
                old.unlink()

            # Track seen paths for duplicate bom_line_id handling
            seen_paths = []
            assignments = {}

            # depth-first assign with index tracking
            def _assign(current_bom, index="0", level=0):
                nonlocal seen_paths, assignments

                lines = current_bom.bom_line_ids.sorted(key=lambda r: (r.sequence or 0, r.id))

                for line_idx, line in enumerate(lines):
                    child = line.child_bom_id
                    if not child:
                        continue

                    # Calculate path index
                    line_index = f"{index}{line_idx}"
                    path_key = f"{root_bom.id}_{line.id}_{line_index}"

                    # Check if this path already processed
                    if path_key in seen_paths:
                        continue

                    # Count existing paths for this bom_line to determine branch
                    existing_count = len([p for p in seen_paths
                                          if p.startswith(f"{root_bom.id}_{line.id}_")])

                    # Get branch code
                    if existing_count >= len(codes):
                        raise UserError(_("No more branch codes available for BOM %s") % root_bom.display_name)

                    code = codes[existing_count]
                    sequence = existing_count + 1

                    _logger.info("Creating mapping for BOM %s line %s path %s -> %s",
                                 root_bom.id, line.id, line_index, code)

                    # Create branch mapping
                    mapping = BranchModel.create({
                        'bom_id': root_bom.id,
                        'bom_line_id': line.id,
                        'branch_name': code,
                        'sequence': sequence,
                        'path_uid': path_key,
                    })

                    # Store assignment
                    assignments[path_key] = mapping.id
                    seen_paths.append(path_key)

                    # Create or reuse location for this branch
                    try:
                        parent = _find_project_parent_location(env)
                        loc_name = f"{code}"

                        loc = Location.create({
                            'name': loc_name,
                            'location_id': parent.id if parent else False,
                            'usage': 'internal',
                        })
                        _logger.info("Created branch location %s (parent %s)",
                                     loc.name, parent.name if parent else None)

                        if loc:
                            mapping.location_id = loc.id

                    except Exception as e:
                        _logger.exception("Failed to create/attach branch location for BOM %s branch %s: %s",
                                          root_bom.id, code, e)

                    # Recurse into child BOM
                    _assign(child, line_index, level + 1)

            # Start assignment from root
            _assign(root_bom, index="0", level=0)

            total = BranchModel.search_count([("bom_id", "=", root_bom.id)])
            _logger.info("Completed BOM %s - Created %s branch mappings", root_bom.id, total)

        except Exception as e:
            _logger.exception("Error processing BOM %s: %s", root_bom.id, e)

    _logger.info("=== assign_branches_after_install END ===")


def _find_project_parent_location(env):
    StockLocation = env['stock.location']

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