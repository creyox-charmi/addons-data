# cr_mrp_bom_customisation/models/mrp_production.py
from odoo import models, fields, api
import logging

from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    branch_mapping_id = fields.Many2one('mrp.bom.line.branch', string='Branch Mapping', help="Branch mapping for this MO (if set, finished goods will go to this branch location)")
    root_bom_id = fields.Many2one("mrp.bom", string="Root BOM", help="Top-level BOM where the chain started.")
    parent_mo_id = fields.Many2one("mrp.production", string="Parent Manufacturing Order")
    can_manufacture = fields.Boolean(
        string="Approved to Manufacture",
        compute="_compute_can_manufacture",
        store=True,
    )
    line = fields.Char(string='Line')
    branch_intermediate_location_id = fields.Many2one(
        'stock.location',
        string='Branch Intermediate Location',
        help='Intermediate branch location before moving to parent'
    )

    def _compute_can_manufacture(self):
        for mo in self:
            # A MO is linked to bom_line via product / child BOM → so:
            line = self.env['mrp.bom.line'].search([
                ('child_bom_id', '=', mo.bom_id.id),
                ('bom_id', '=', mo.root_bom_id.id),
            ], limit=1)

            mo.can_manufacture = line.approve_to_manufacture if line else False


    # def action_confirm(self):
    #     self._check_approve_to_manufacture()
    #
    #     res = super().action_confirm()
    #
    #     for mo in self:
    #         # Get the branch destination location from the MO
    #         branch_location = mo.location_dest_id
    #
    #         if branch_location:
    #             # Update finished product move lines
    #             for move in mo.move_finished_ids:
    #                 if move.move_line_ids:
    #                     move.move_line_ids.write({
    #                         'location_dest_id': branch_location.id
    #                     })
    #
    #             # Update component/raw material move lines
    #             for move in mo.move_raw_ids:
    #                 if move.move_line_ids:
    #                     move.move_line_ids.write({
    #                         'location_dest_id': branch_location.id
    #                     })
    #
    #     return res

    def action_confirm(self):
        self._check_approve_to_manufacture()
        res = super().action_confirm()
        for mo in self:
            own_branch = mo.branch_intermediate_location_id
            parent_branch = mo.location_dest_id

            if own_branch and parent_branch:
                # Update finished product move lines: Own branch → Parent branch
                for move in mo.move_finished_ids:
                    move.write({
                        'location_id': own_branch.id,
                        'location_dest_id': parent_branch.id,
                    })
                    if move.move_line_ids:
                        move.move_line_ids.write({
                            'location_id': own_branch.id,
                            'location_dest_id': parent_branch.id,
                        })

                # Update raw material move lines: Source (as is) → Own branch
                for move in mo.move_raw_ids:
                    move.write({
                        'location_dest_id': own_branch.id,
                    })
                    if move.move_line_ids:
                        move.move_line_ids.write({
                            'location_dest_id': own_branch.id,
                        })

        return res


    # def _create_update_move_finished(self):
    #     """Override to ensure branch location is applied to finished moves"""
    #     moves = super()._create_update_move_finished()
    #
    #     # Apply branch location if exists
    #     branch_location = self.location_dest_id
    #     if branch_location and moves:
    #         moves.write({
    #             'location_dest_id': branch_location.id
    #         })
    #
    #     return moves

    # def _create_update_move_finished(self):
    #     """Override to set intermediate branch location for finished product"""
    #     moves = super()._create_update_move_finished()
    #
    #     # Update finished move to go to intermediate location first
    #     if self.branch_intermediate_location_id and moves:
    #         moves.write({
    #             'location_dest_id': self.branch_intermediate_location_id.id
    #         })
    #
    #     return moves

    def _create_update_move_finished(self):
        """Override to set THREE-LOCATION flow for finished product"""
        moves = super()._create_update_move_finished()

        own_branch = self.branch_intermediate_location_id  # Own branch
        parent_branch = self.location_dest_id  # Parent branch

        if own_branch and parent_branch and moves:
            for move in moves:
                move.write({
                    'location_id': own_branch.id,  # Source: Own branch
                    'location_dest_id': parent_branch.id,  # Destination: Parent branch
                })
                print(f"[DEBUG] Finished move for {self.name}:")
                print(f"  Source (location_id): {move.location_id.display_name}")
                print(f"  Destination (location_dest_id): {move.location_dest_id.display_name}")

        return moves


    # def _get_moves_raw_values(self):
    #     """Override to set branch location for raw material moves"""
    #     moves_raw_values = super()._get_moves_raw_values()
    #
    #     branch_location = self.location_dest_id
    #     if branch_location:
    #         for move_vals in moves_raw_values:
    #             move_vals['location_dest_id'] = branch_location.id
    #
    #     return moves_raw_values

    def _get_moves_raw_values(self):
        """Override to set correct locations for raw material moves:
        Source: As is (stock) → Destination: Own Branch"""
        moves_raw_values = super()._get_moves_raw_values()

        own_branch = self.branch_intermediate_location_id

        if own_branch:
            for move_vals in moves_raw_values:
                # Components: Keep source as is, destination = own branch
                move_vals['location_dest_id'] = own_branch.id
                print(f"[DEBUG] Raw material move: {move_vals.get('product_id')} → {own_branch.display_name}")

        return moves_raw_values




    def button_unreserve(self):
        self._check_approve_to_manufacture()
        return super().button_unreserve()

    def action_scrap(self):
        self._check_approve_to_manufacture()
        return super().action_scrap()

    # def _check_approve_to_manufacture(self):
    #     for mo in self:
    #
    #         # CASE 1: Normal MOs → NO restriction
    #         if not mo.root_bom_id:
    #             return  # normal MO, allow everything
    #
    #         # CASE 2: Find related BOM line
    #         line = self.env['mrp.bom.line'].search([
    #             ('child_bom_id', '=', mo.bom_id.id),
    #             ('bom_id', '=', mo.root_bom_id.id),
    #         ], limit=1)
    #
    #         allowed = line.approve_to_manufacture if line else False
    #
    #         # CASE 3: If not approved → BLOCK
    #         if not allowed:
    #             raise UserError(
    #                 f"Operation not allowed.\n"
    #                 f"This MO belongs to an EVR recursive BOM but the related line is NOT approved.\n"
    #                 f"Please enable 'Approve to Manufacture' on the BOM line."
    #             )



    def _check_approve_to_manufacture(self):
        for mo in self:
            if mo.root_bom_id and self.line:
                bom = mo.bom_id

                print("\n==========================")
                print(f"🔍 Checking approval for MO: {mo.name}")
                print(f"   BOM: {bom.display_name} (ID {bom.id})")
                print("==========================")

                line = self.env['mrp.bom.line'].search([
                                ('product_id', '=', self.product_id.id),
                                ('id','=',int(self.line))
                            ], limit=1)
                # print('bom_id : ', mo.bom_id)
                print('line : ',line,' ',line.approve_to_manufacture)
                is_main_allowed = line.approve_to_manufacture if line else False
                print('is_main_allowed : ', is_main_allowed)
                if is_main_allowed:
                    allowed = self._check_descendant_approval(bom)

                    print(f"➡️ Result for MO {mo.name}: allowed = {allowed}")

                    if not allowed:
                        print(f"❌ Approval FAILED for MO {mo.name}")
                        raise UserError(
                            "You cannot perform this operation because not all BOM lines "
                            "below this MO are approved for manufacture.\n\n"
                            "Please enable 'Approve to Manufacture' on all child BOM lines."
                        )
                else:
                    raise UserError(
                        "You cannot perform this operation because not all BOM lines "
                        "below this MO are approved for manufacture.\n\n"
                        "Please enable 'Approve to Manufacture' on all child BOM lines."
                    )

    def _check_descendant_approval(self, bom):
        """
        Check approval ONLY for lines that have a child BOM.
        """
        print(f"\n   🔎 Checking BOM: {bom.display_name} (ID {bom.id}) for descendant approval...")

        lines = self.env['mrp.bom.line'].search([
            ('bom_id', '=', bom.id),
        ])

        for line in lines:

            # Skip lines that do NOT have child BOM
            if not line.child_bom_id:
                print(
                    f"      ➤ Line {line.id} | Product: {line.product_id.display_name} "
                    f"| No child BOM → SKIP"
                )
                continue

            # Only check lines that HAVE child BOM
            print(
                f"      ➤ Line {line.id} | Product: {line.product_id.display_name} | "
                f"Approve? {line.approve_to_manufacture} | "
                f"Child BOM: {line.child_bom_id.display_name}"
            )

            # If this line with child BOM is NOT approved → FAIL
            if not line.approve_to_manufacture:
                print(f"      ❌ FAILED at BOM line {line.id} → Not approved")
                return False

            # If approved and has child BOM → go deeper
            print(f"      🔽 Going deeper into child BOM: {line.child_bom_id.display_name} (ID {line.child_bom_id.id})")
            if not self._check_descendant_approval(line.child_bom_id):
                return False

        print(f"   ✅ All child-BOM lines under BOM {bom.display_name} are approved.")
        return True

    def move_finished_to_branch(self):
        """Move finished product quantity from production output location to branch location."""
        for prod in self:
            if not prod.branch_mapping_id or not prod.branch_mapping_id.location_id:
                _logger.info("No branch mapping/location set for production %s", prod.name)
                continue

            dest_location = prod.branch_mapping_id.location_id
            # Find final moves (finished moves) for this production
            finished_moves = prod.move_finished_ids.filtered(lambda m: m.state in ('draft','confirmed','waiting') or m.state == 'done')
            if not finished_moves:
                # sometimes finished moves are in move_raw_work or move_finished_ids, try move_raw_ids_by_finished or stock pickings
                finished_moves = prod.move_finished_ids

            if not finished_moves:
                _logger.warning("No finished moves found for production %s", prod.name)
                continue

            # For safety, create a transfer of the produced qty from current destination to branch location
            for mv in finished_moves:
                # Skip if already at desired location
                if mv.location_dest_id.id == dest_location.id:
                    _logger.info("Move %s already has destination %s", mv.id, dest_location.name)
                    continue

                # Best practice: create a new stock.picking or move to move the quantity
                # Here we will create a new internal move that moves product from current dest to branch location.
                try:
                    move_vals = {
                        'name': f"Move to branch {prod.branch_mapping_id.branch_name} for {prod.name}",
                        'product_id': mv.product_id.id,
                        'product_uom_qty': mv.product_uom_qty,
                        'product_uom': mv.product_uom.id,
                        'location_id': mv.location_dest_id.id,
                        'location_dest_id': dest_location.id,
                        'company_id': prod.company_id.id,
                        'origin': prod.name,
                    }
                    new_move = self.env['stock.move'].create(move_vals)
                    # Confirm & assign & done quickly (depends on your workflow)
                    new_move._action_confirm()
                    new_move._action_assign()
                    new_move._action_done()
                    _logger.info("Moved produced product %s to branch location %s (move %s)", mv.product_id.display_name, dest_location.name, new_move.id)
                    print(f"Moved produced product to branch {dest_location.name} (move {new_move.id})")
                except Exception as e:
                    _logger.exception("Failed to create branch move for production %s: %s", prod.name, e)

    # Example: call move_finished_to_branch after production is marked 'done'.
    # Hook depends on your exact Odoo version and how you finalize production.
    # We add an override of button_mark_done if present, but keep it safe.
    # def button_mark_done(self):
    #     res = super().button_mark_done()
    #     try:
    #         self.move_finished_to_branch()
    #     except Exception as e:
    #         _logger.exception("Error moving finished to branch after mark_done: %s", e)
    #     return res



    def _get_approved_bom_lines(self, bom):
        """
        Get only approved BOM lines (where all children are approved)
        """
        approved_lines = self.env['mrp.bom.line']

        for line in bom.bom_line_ids:
            if bom._check_all_children_approved(line):
                approved_lines |= line

        return approved_lines

    # @api.model
    # def create(self, vals):
    #     if vals.get('bom_id'):
    #         bom = self.env['mrp.bom'].browse(vals['bom_id'])
    #         if bom.is_evr:
    #             unapproved_lines = []
    #
    #             if bom.project_id:
    #                 vals['project_id'] = bom.project_id.id
    #
    #             for line in bom.bom_line_ids:
    #                 if not bom._check_all_children_approved(line):
    #                     unapproved_lines.append(line.product_id.display_name)
    #
    #             if unapproved_lines:
    #                 raise ValidationError(
    #                     "Cannot create MO. The following BOM lines or their sub-components are not approved for manufacture:\n" +
    #                     "\n".join([f"- {name}" for name in unapproved_lines])
    #                 )
    #
    #     branch_dest_location = self.env.context.get('branch_dest_location')
    #
    #     mo = super().create(vals)
    #
    #     # Update ALL moves (finished + components) with branch location
    #     if branch_dest_location:
    #         # Finished product moves
    #         if mo.move_finished_ids:
    #             mo.move_finished_ids.write({
    #                 'location_dest_id': branch_dest_location
    #             })
    #
    #         # Raw material/component moves - update source location
    #         if mo.move_raw_ids:
    #             mo.move_raw_ids.write({
    #                 'location_dest_id': branch_dest_location  # Components consumed to branch location
    #             })
    #
    #     return mo

    @api.model
    def create(self, vals):
        if vals.get('bom_id'):
            bom = self.env['mrp.bom'].browse(vals['bom_id'])
            if bom.is_evr:
                unapproved_lines = []

                if bom.project_id:
                    vals['project_id'] = bom.project_id.id

                for line in bom.bom_line_ids:
                    if not bom._check_all_children_approved(line):
                        unapproved_lines.append(line.product_id.display_name)

                if unapproved_lines:
                    raise ValidationError(
                        "Cannot create MO. The following BOM lines or their sub-components are not approved for manufacture:\n" +
                        "\n".join([f"- {name}" for name in unapproved_lines])
                    )

        branch_intermediate_location = self.env.context.get('branch_intermediate_location')
        branch_final_location = self.env.context.get('branch_final_location')

        # Store intermediate location
        if branch_intermediate_location:
            vals['branch_intermediate_location_id'] = branch_intermediate_location

        mo = super().create(vals)


        return mo


