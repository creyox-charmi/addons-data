# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'


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

            # # For raw material moves: Keep source, destination = own branch
            # elif self in self.production_id.move_raw_ids and own_branch:
            #     vals['location_dest_id'] = own_branch.id

        return vals

    def _action_confirm(self, merge=True, merge_into=False):
        """Override to maintain branch locations when move is confirmed"""
        res = super()._action_confirm(merge=merge, merge_into=merge_into)

        for move in self:
            if move.production_id:

                own_branch = move.production_id.branch_intermediate_location_id
                parent_branch = move.production_id.location_dest_id

                # for data in move.production_id.move_raw_ids:
                #
                #     child_mo = self.env['mrp.production'].search([
                #         ('parent_mo_id', '=', move.production_id.id),
                #         ('product_tmpl_id', '=', data.product_id.product_tmpl_id.id),
                #     ], limit=1)
                #
                #     if child_mo:
                #         data.write({
                #             'location_id': own_branch.id,
                #         })


                # Finished product moves
                if move in move.production_id.move_finished_ids and own_branch and parent_branch:

                    if move.location_id != own_branch or move.location_dest_id != parent_branch:
                        move.write({
                            'location_id': own_branch.id,
                            'location_dest_id': parent_branch.id,
                        })

                # # Raw material moves
                # elif move in move.production_id.move_raw_ids and own_branch:
                #     if move.location_dest_id != own_branch:
                #         move.write({
                #             'location_dest_id': own_branch.id,
                #         })

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

                    # # Raw material move lines
                    # elif move in move.production_id.move_raw_ids and own_branch:
                    #     move.move_line_ids.write({
                    #         'location_dest_id': own_branch.id,
                    #     })

        return res


