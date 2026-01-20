from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    cfe = fields.Boolean(string="CFE")

    def button_confirm(self):
        print("\n=========== PO CONFIRM TRIGGERED ===========")

        res = super().button_confirm()

        for order in self:
            print(f"\n--- Processing PO: {order.name} ---")
            print(f"CFE Value: {order.cfe}")
            print(f"Vendor: {order.partner_id.name}")

            if order.cfe:
                vendor = order.partner_id

                # Pickings
                pickings = order.picking_ids
                print(f"Found {len(pickings)} pickings for this PO")

                for pk in pickings:
                    print(f"  -> Setting owner on picking: {pk.name}")

                pickings.write({"owner_id": vendor.id})

                # Move Lines (Detailed operations)
                move_lines = pickings.mapped("move_line_ids")
                print(f"Found {len(move_lines)} move lines")

                for ml in move_lines:
                    print(f"  -> Setting owner on move line: {ml.id}, product: {ml.product_id.name}")

                move_lines.write({"owner_id": vendor.id})

                print(">>> Owner updated successfully for pickings & move lines")

            else:
                print("CFE is FALSE → No owner assignment")

        print("=========== PO CONFIRM END ===========\n")
        return res