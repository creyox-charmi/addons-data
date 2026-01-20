from odoo import models

class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()
        print(f"\n🔵 [_prepare_procurement_values] called for Move ID {self.id}")
        print(f"   • Product: {self.product_id.display_name} (ID {self.product_id.id})")
        print(f"   • From MO: {self.raw_material_production_id.display_name if self.raw_material_production_id else 'N/A'}")
        print(f"   • BOM Line: {self.bom_line_id.display_name if self.bom_line_id else 'N/A'}")

        if self.bom_line_id and self.raw_material_production_id:
            values.update({
                "bom_id": self.raw_material_production_id.bom_id.id,
                "bom_line_id": self.bom_line_id.id,
            })
            print(f"   ✅ Injected BOM Info → bom_id={values['bom_id']}, bom_line_id={values['bom_line_id']}")
        else:
            print("   ⚠️ No BOM info found → Skipping injection")

        print(f"   🔎 Final values dict: {values}")
        return values
