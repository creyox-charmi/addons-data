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

    def action_cancel(self):
        print("CALLLLL")
        for production in self:
            # Reverse the quantity of actual product -- BOM using revere move line of product
            for move in production.move_finished_ids:
                if move.state == 'done':
                    return_picking = self.env['stock.picking'].create({
                        'picking_type_id': move.picking_type_id.id,
                        'location_id': move.location_dest_id.id,
                        'location_dest_id': move.location_id.id,
                    })
                    return_move = self.env['stock.move'].create({
                        'name': move.name,
                        'product_id': move.product_id.id,
                        'product_uom_qty': move.product_qty,
                        'picking_id': return_picking.id,
                        'location_id': move.location_dest_id.id,
                        'location_dest_id': move.location_id.id,
                    })
                    return_picking.action_assign()
                    return_picking.button_validate()
                else:
                    move._do_unreserve()
                    move._action_cancel()

                for move in production.move_raw_ids:
                    move.quantity = move.quantity - move.quantity
                    for line in move.move_line_ids:
                        line.write({'state': 'draft'})
                        line.unlink()

                journals_mrp = self.env["account.move.line"].search(
                    [("product_id", "=", production.product_id.id)]
                )
                for journal in journals_mrp:
                    if journal.move_id.state == "posted":
                        journal.move_id.button_draft()
                    journal.unlink()

                components_stock_moves = self.env["stock.move"].search(
                    [("raw_material_production_id", "=", production.id)]
                )
                for stock_move in components_stock_moves:
                    journals_component = self.env["account.move.line"].search(
                        [("product_id", "=", stock_move.product_id.id)]
                    )
                    for journal in journals_component:
                        if journal.move_id.state == "posted":
                            journal.move_id.button_draft()
                        journal.unlink()


                # # Handle accounting entries for the production order
                # account_moves_main = self.env["account.move"].search(
                #     [("stock_move_id", "in", production.move_finished_ids.ids)]
                # )
                # print('account_moves_main : ',account_moves_main)
                # account_moves_components = self.env["account.move"].search(
                #     [("stock_move_id", "in", production.move_raw_ids.ids)]
                # )
                # print('account_moves_components : ', account_moves_components)
                # for account_move in account_moves_main:
                #     if account_move.state == "posted":
                #         account_move.button_draft()
                #     account_move.unlink()
                #
                # for account_move_sub in account_moves_components:
                #     if account_move_sub.state == "posted":
                #         account_move_sub.button_draft()
                #     account_move_sub.unlink()
                #
                # for move in production.move_raw_ids:
                #     move.quantity = move.quantity - move.quantity
                #     for line in move.move_line_ids:
                #         line.write({'state': 'draft'})
                #         line.unlink()

            production.write({"state": "cancel"})