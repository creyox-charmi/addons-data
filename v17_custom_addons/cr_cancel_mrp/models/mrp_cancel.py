from odoo import api, fields, models


class MrpCancellation(models.Model):
    _inherit = "mrp.production"

    # Resetting the state of MO to Draft
    def action_reset_to_draft(self):
        if self.state == "done":
            self.action_cancel()
        self.state = "draft"
        context = dict(self._context)
        context["reset_to_draft"] = True
        self.with_context(context)._compute_state()

    def _compute_state(self):
        if self._context.get("reset_to_draft"):
            self.state = "draft"
        else:
            super(MrpCancellation, self)._compute_state()

    # Cancel the MO & journal and then delete them
    def action_cancel(self):
        for production in self:
            # Reverse finished product stock moves
            for move in production.move_finished_ids:
                if move.state == "done":
                    # Attempt to use the return picking type if available
                    return_picking_type = (
                        move.picking_type_id.return_picking_type_id
                        or self.env.ref("stock.picking_type_in")
                    )

                    # Create a return picking
                    return_picking = self.env["stock.picking"].create(
                        {
                            "picking_type_id": return_picking_type.id,
                            "location_id": move.location_dest_id.id,
                            "location_dest_id": move.location_id.id,
                            "origin": f"Return of {move.reference}",
                        }
                    )

                    # Create a return stock move
                    return_move = self.env["stock.move"].create(
                        {
                            "name": f"Return of {move.name}",
                            "product_id": move.product_id.id,
                            "product_uom_qty": move.product_qty,
                            "product_uom": move.product_uom.id,
                            "picking_id": return_picking.id,
                            "location_id": move.location_dest_id.id,
                            "location_dest_id": move.location_id.id,
                        }
                    )
                    return_move._action_confirm()
                    return_move._action_done()
                else:
                    # For moves not in 'done' state, unreserve and cancel
                    move._do_unreserve()
                    move._action_cancel()

            # Reverse raw material stock moves
            for move in production.move_raw_ids:
                if move.state == "done":
                    return_picking_type = (
                        move.picking_type_id.return_picking_type_id
                        or self.env.ref("stock.picking_type_in")
                    )
                    return_picking = self.env["stock.picking"].create(
                        {
                            "picking_type_id": return_picking_type.id,
                            "location_id": move.location_dest_id.id,
                            "location_dest_id": move.location_id.id,
                            "origin": f"Return of {move.reference}",
                        }
                    )
                    return_move = self.env["stock.move"].create(
                        {
                            "name": f"Return of {move.name}",
                            "product_id": move.product_id.id,
                            "product_uom_qty": move.product_qty,
                            "product_uom": move.product_uom.id,
                            "picking_id": return_picking.id,
                            "location_id": move.location_dest_id.id,
                            "location_dest_id": move.location_id.id,
                        }
                    )
                    return_move._action_confirm()
                    return_move._action_done()
                else:
                    # For non-done moves, cancel directly
                    move._action_cancel()

            # Handle accounting entries for the production order
            account_moves_main = self.env["account.move"].search(
                [("stock_move_id", "in", production.move_finished_ids.ids)]
            )
            account_moves_components = self.env["account.move"].search(
                [("stock_move_id", "in", production.move_raw_ids.ids)]
            )
            for account_move in account_moves_main:
                if account_move.state == "posted":
                    account_move.button_draft()
                account_move.unlink()

            for account_move_sub in account_moves_components:
                if account_move_sub.state == "posted":
                    account_move_sub.button_draft()
                account_move_sub.unlink()

            # Update the production state to 'cancel'
            production.write({"state": "cancel"})
