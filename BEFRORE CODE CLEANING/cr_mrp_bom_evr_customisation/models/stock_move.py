# models/stock_move.py
from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    # def _action_confirm(self, merge=True, merge_into=False):
    #     """Override to maintain branch location when move is confirmed"""
    #     res = super()._action_confirm(merge=merge, merge_into=merge_into)
    #
    #     for move in self:
    #         # If this move belongs to an MO with branch location
    #         if move.production_id and move.production_id.location_dest_id:
    #             branch_location = move.production_id.location_dest_id
    #
    #             # Update destination for both finished and raw moves
    #             if move.location_dest_id != branch_location:
    #                 move.location_dest_id = branch_location
    #
    #         # Also check for raw material consumption (raw_material_production_id)
    #         if move.raw_material_production_id and move.raw_material_production_id.location_dest_id:
    #             branch_location = move.raw_material_production_id.location_dest_id
    #             if move.location_dest_id != branch_location:
    #                 move.location_dest_id = branch_location
    #
    #     return res
    #
    # def _create_move_lines(self):
    #     """Override to apply branch location to all move lines"""
    #     res = super()._create_move_lines()
    #
    #     for move in self:
    #         branch_location = None
    #
    #         # Check for finished product moves
    #         if move.production_id and move.production_id.location_dest_id:
    #             branch_location = move.production_id.location_dest_id
    #
    #         # Check for raw material moves
    #         elif move.raw_material_production_id and move.raw_material_production_id.location_dest_id:
    #             branch_location = move.raw_material_production_id.location_dest_id
    #
    #         # Update all move lines (including those with lot/serial) with branch location
    #         if branch_location and move.move_line_ids:
    #             move.move_line_ids.write({
    #                 'location_dest_id': branch_location.id
    #             })
    #
    #     return res

    # def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
    #     """Override to set branch location in move line vals during creation"""
    #     vals = super()._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
    #
    #     branch_location = None
    #
    #     # Check for production moves
    #     if self.production_id and self.production_id.location_dest_id:
    #         branch_location = self.production_id.location_dest_id
    #     elif self.raw_material_production_id and self.raw_material_production_id.location_dest_id:
    #         branch_location = self.raw_material_production_id.location_dest_id
    #
    #     if branch_location:
    #         vals['location_dest_id'] = branch_location.id
    #
    #     return vals

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        """Set branch locations in move line vals during creation"""
        vals = super()._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)

        if self.production_id:
            own_branch = self.production_id.branch_intermediate_location_id
            parent_branch = self.production_id.location_dest_id

            # For finished product moves: Own branch → Parent branch
            if self in self.production_id.move_finished_ids and own_branch and parent_branch:
                vals['location_id'] = own_branch.id
                vals['location_dest_id'] = parent_branch.id

            # For raw material moves: Keep source, destination = own branch
            elif self in self.production_id.move_raw_ids and own_branch:
                vals['location_dest_id'] = own_branch.id

        return vals

    def _action_confirm(self, merge=True, merge_into=False):
        """Override to maintain branch locations when move is confirmed"""
        res = super()._action_confirm(merge=merge, merge_into=merge_into)

        for move in self:
            if move.production_id:

                own_branch = move.production_id.branch_intermediate_location_id
                parent_branch = move.production_id.location_dest_id

                # child_mo = self.env['mrp.production'].search([
                #     ('parent_mo_id', '=', move.production_id.id),
                #     ('product_tmpl_id', '=', move.product_id.product_tmpl_id.id),
                # ], limit=1)
                # print('move.product_id.product_tmpl_id.id : ',move.product_id.product_tmpl_id.id)
                # print('move.production_id.id : ',move.production_id.id)
                # print('move : ',move)
                # print('child_mo : ', child_mo)
                print('move.production_id.move_raw_ids : ',move.production_id.move_raw_ids)
                print('move.production_id.move_finished_ids : ', move.production_id.move_finished_ids)
                # print('==============child_mo================')
                # if child_mo:
                #     move.write({
                #         'location_id': own_branch.id,
                #     })

                for data in move.production_id.move_raw_ids:
                    print('data : ',data)
                    child_mo = self.env['mrp.production'].search([
                        ('parent_mo_id', '=', move.production_id.id),
                        ('product_tmpl_id', '=', data.product_id.product_tmpl_id.id),
                    ], limit=1)
                    print('child_mo : ', child_mo)
                    if child_mo:
                        data.write({
                            'location_id': own_branch.id,
                        })


                # Finished product moves
                if move in move.production_id.move_finished_ids and own_branch and parent_branch:

                    if move.location_id != own_branch or move.location_dest_id != parent_branch:
                        move.write({
                            'location_id': own_branch.id,
                            'location_dest_id': parent_branch.id,
                        })

                # Raw material moves
                elif move in move.production_id.move_raw_ids and own_branch:
                    if move.location_dest_id != own_branch:
                        move.write({
                            'location_dest_id': own_branch.id,
                        })

        return res

    def _create_move_lines(self):
        """Override to apply branch locations to all move lines"""
        res = super()._create_move_lines()

        for move in self:
            if move.production_id:
                own_branch = move.production_id.branch_intermediate_location_id
                parent_branch = move.production_id.location_dest_id

                if move.move_line_ids:
                    # Finished product move lines
                    if move in move.production_id.move_finished_ids and own_branch and parent_branch:
                        move.move_line_ids.write({
                            'location_id': own_branch.id,
                            'location_dest_id': parent_branch.id,
                        })

                    # Raw material move lines
                    elif move in move.production_id.move_raw_ids and own_branch:
                        move.move_line_ids.write({
                            'location_dest_id': own_branch.id,
                        })

        return res


