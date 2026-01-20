# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models,fields

class StockPicking(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):
        res = super().button_validate()

        for move in self.move_ids_without_package:
            so_line = move.sale_line_id
            if not so_line:
                continue

            if so_line.re_nre == 're':
                # RE → normal sync
                so_line.action_sync_re_sub_lines(
                    delivery_name=move.picking_id.name if move.picking_id else None,
                )
            # elif so_line.re_nre == 'nre':
            #     # NRE → update ALL sub-lines with delivery date
            #     if so_line.nre_sub_line_ids:
            #         so_line.nre_sub_line_ids.write({
            #             "updated_delivery_date": fields.Date.today(),
            #         })

        return res
