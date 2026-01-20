from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):
        print("🟢 [Custom _run_buy] called with procurements:", len(procurements))

        filtered_procurements = []

        for procurement, rule in procurements:
            product = procurement.product_id
            values = procurement.values

            print(f"➡️ Processing Procurement: Product={product.display_name}, ID={product.id}")

            bom_id = values.get("bom_id")
            bom_line_id = values.get("bom_line_id")
            related_mo_id = self.env['mrp.production'].browse(int(values.get("production_id"))).id
            print("   🔎 bom_id:", bom_id, "| bom_line_id:", bom_line_id)

            skip_procurement = False

            if bom_id and bom_line_id:
                # Check if active session context has po_created=True
                active_ctx = self.env["mrp.bom.context"].search([
                    ("root_bom_id", "=", bom_id),
                    ("bom_line_id", "=", bom_line_id),
                    ("related_mo_id", "=", related_mo_id)
                ])
                print('active_ctx :: ',active_ctx)


                if active_ctx and active_ctx.po_created:
                    print("   ✅ Active session context shows PO already created")
                    skip_procurement = True
                    # existing_pos = self._check_existing_evr_pos(product, bom_id, related_mo_id)
                    # if existing_pos:
                    #     print(f"   📌 Found existing EVR POs: {len(existing_pos)}")
                    #     skip_procurement = True

                else:
                    # Also check for existing EVR POs
                    existing_pos = self._check_existing_evr_pos(product, bom_id,related_mo_id)
                    if existing_pos:
                        print(f"   📌 Found existing EVR POs: {len(existing_pos)}")
                        skip_procurement = True
                        # Update active context to reflect PO exists
                        if active_ctx:
                            active_ctx.po_created = True

            if skip_procurement:
                print("   ⏩ Skipping procurement → PO already exists")
                continue

            filtered_procurements.append((procurement, rule))

        if filtered_procurements:
            print(f"🚀 Passing remaining procurements to super()._run_buy → {len(filtered_procurements)}")
            return super()._run_buy(filtered_procurements)

        print("✅ No procurements left to process → all were skipped (already handled)")
        return True

    def _check_existing_evr_pos(self, product, bom_id,related_mo_id):
        """Check if POs already exist for this product from EVR flows"""
        bom = self.env['mrp.bom'].browse(bom_id)
        if not bom.exists():
            return False

        # Get BOM product info for origin matching
        product_code = bom.product_id.default_code or bom.product_tmpl_id.default_code or ''
        product_name = bom.product_id.name or bom.product_tmpl_id.name or ''

        # Check for vendor POs
        vendor_pos = self.env['purchase.order'].search([
            ('order_line.product_id', '=', product.id),
            ('state', 'in', ['draft', 'sent', 'to approve', 'purchase']),
            '|',  # OR condition
            ('origin', 'like', f'BOM [{product_code}] {product_name}'),
            ('origin', 'like', f'Vendor-Instant - {product_name}'),
            ('production_id','=',related_mo_id)
        ])


        return vendor_pos


