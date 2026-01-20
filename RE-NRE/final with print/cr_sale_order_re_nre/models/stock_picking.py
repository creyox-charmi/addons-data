from datetime import date
from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    # def button_validate(self):
    #     res = super().button_validate()
    #
    #     for move in self.move_ids_without_package:
    #         so_line = move.sale_line_id
    #         if not so_line:
    #             continue
    #
    #         # 1️⃣ Update main line updated_delivery_date if fully delivered
    #         if so_line.product_uom_qty > 0 and so_line.qty_delivered >= so_line.product_uom_qty:
    #             if not so_line.updated_delivery_date:
    #                 so_line.write({'updated_delivery_date': date.today()})
    #                 print(f"[DEBUG] Updated delivery date set for SO Line {so_line.id}")
    #
    #         # 2️⃣ Sync RE sub-lines if line is RE
    #         if so_line.re_nre == 're':
    #             print(f"[DEBUG] Syncing RE sub-lines for SO Line {so_line.id}")
    #             so_line.action_sync_re_sub_lines(delivery_date=date.today())
    #
    #     return res

    def button_validate(self):
        res = super().button_validate()

        for move in self.move_ids_without_package:
            so_line = move.sale_line_id
            if not so_line:
                continue

            # # 1️⃣ Update main line updated_delivery_date if fully delivered
            # if so_line.product_uom_qty > 0 and so_line.qty_delivered >= so_line.product_uom_qty:
            #     if not so_line.updated_delivery_date:
            #         so_line.write({'updated_delivery_date': date.today()})
            #         print(f"[DEBUG] Updated delivery date set for SO Line {so_line.id}")

            # 2️⃣ Sync RE sub-lines if line is RE
            if so_line.re_nre == 're':
                print(f"[DEBUG] Syncing RE sub-lines for SO Line {so_line.id}")
                # Pass the delivery/picking name here
                print(f"move {move}")
                print(f"move.picking_id {move.picking_id}")
                print(f"move.picking_id.name {move.picking_id.name}")
                so_line.action_sync_re_sub_lines(delivery_name=move.picking_id.name if move.picking_id else None)

        return res
