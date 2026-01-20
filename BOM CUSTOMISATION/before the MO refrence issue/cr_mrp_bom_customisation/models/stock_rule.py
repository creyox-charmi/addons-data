from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockRule(models.Model):
    _inherit = 'stock.rule'

    # @api.model
    # def _run_buy(self, procurements):
    #     print('xsjxdowjdsxwkedes111111111111')
    #     _logger.info("🔍 Custom _run_buy() called with procurements count: %s", len(procurements))
    #     filtered_procurements = []
    #
    #     for procurement, rule in procurements:
    #         product = procurement.product_id
    #         values = procurement.values
    #         _logger.info("➡️ Processing procurement for product %s (%s)", product.id, product.display_name)
    #
    #         bom_id = values.get("bom_id")
    #         print('bom_id : ',bom_id)
    #         bom_line_id = values.get("bom_line_id")
    #         print('bom_line_id : ', bom_line_id)
    #
    #         if bom_id and bom_line_id:
    #             ctx = self.env['mrp.bom.context'].search([
    #                 ('root_bom_id', '=', bom_id),
    #                 ('bom_line_id', '=', bom_line_id),
    #             ], limit=1)
    #
    #             if ctx:
    #                 _logger.info("🔎 Found BOM Context → po_created=%s", ctx.po_created)
    #                 if ctx.po_created:
    #                     _logger.info("⏩ Skipping procurement (already handled by custom PO creation)")
    #                     continue
    #
    #         filtered_procurements.append((procurement, rule))
    #
    #     if filtered_procurements:
    #         _logger.info("🚀 Passing %s procurements to super()._run_buy()", len(filtered_procurements))
    #         return super()._run_buy(filtered_procurements)
    #
    #     _logger.info("✅ No procurements left to process (all handled by context)")
    #     return True

    # @api.model
    # def _run_buy(self, procurements):
    #     print("🟢 [Custom _run_buy] called with procurements:", len(procurements))
    #     _logger.info("🟢 [Custom _run_buy] called with procurements count: %s", len(procurements))
    #
    #     filtered_procurements = []
    #
    #     for procurement, rule in procurements:
    #         product = procurement.product_id
    #         values = procurement.values
    #
    #         print(f"➡️ Processing Procurement: Product={product.display_name}, ID={product.id}")
    #         _logger.info("➡️ Processing procurement for product %s (%s)", product.id, product.display_name)
    #
    #         bom_id = values.get("bom_id")
    #         bom_line_id = values.get("bom_line_id")
    #         print("   🔎 bom_id:", bom_id, "| bom_line_id:", bom_line_id)
    #
    #         if bom_id and bom_line_id:
    #             ctx = self.env["mrp.bom.context"].search([
    #                 ("root_bom_id", "=", bom_id),
    #                 ("bom_line_id", "=", bom_line_id),
    #             ], limit=1)
    #
    #             if ctx:
    #                 print(f"   📌 Context found → po_created={ctx.po_created}")
    #                 _logger.info("   📌 BOM Context found → po_created=%s", ctx.po_created)
    #
    #                 # 🚫 Restrict PO if already created by custom process
    #                 if ctx.po_created:
    #                     print("   ⏩ Skipping procurement → Vendor PO already created")
    #                     _logger.info("   ⏩ Skipping procurement → Vendor PO already created by custom flow")
    #                     continue
    #
    #         # If no context or not yet created → allow normal procurement
    #         filtered_procurements.append((procurement, rule))
    #
    #     if filtered_procurements:
    #         print("🚀 Passing remaining procurements to super()._run_buy →", len(filtered_procurements))
    #         _logger.info("🚀 Passing %s procurements to super()._run_buy()", len(filtered_procurements))
    #         return super()._run_buy(filtered_procurements)
    #
    #     print("✅ No procurements left to process → all were skipped (already handled)")
    #     _logger.info("✅ No procurements left to process → all handled by custom PO creation")
    #     return True

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
            print("   🔎 bom_id:", bom_id, "| bom_line_id:", bom_line_id)

            skip_procurement = False

            if bom_id and bom_line_id:
                # Check context first
                ctx = self.env["mrp.bom.context"].search([
                    ("root_bom_id", "=", bom_id),
                    ("bom_line_id", "=", bom_line_id),
                ], limit=1)

                # if ctx and ctx.po_created:
                #     print(f"   📌 Context found → po_created={ctx.po_created}")
                #     skip_procurement = True
                # else:
                #     # Additional check: Look for existing POs with EVR origins
                #     existing_pos = self._check_existing_evr_pos(product, bom_id)
                #     if existing_pos:
                #         print(f"   📌 Found existing EVR POs: {len(existing_pos)}")
                #         skip_procurement = True
                #         # Update context to reflect PO exists
                #         if ctx:
                #             ctx.po_created = True

                existing_pos = self._check_existing_evr_pos(product, bom_id)
                if existing_pos:
                    print(f"   📌 Found existing EVR POs: {len(existing_pos)}")
                    skip_procurement = True
                    # Update context to reflect PO exists
                    if ctx:
                        ctx.po_created = True

            if skip_procurement:
                print("   ⏩ Skipping procurement → PO already exists")
                continue

            filtered_procurements.append((procurement, rule))

        if filtered_procurements:
            print(f"🚀 Passing remaining procurements to super()._run_buy → {len(filtered_procurements)}")
            return super()._run_buy(filtered_procurements)

        print("✅ No procurements left to process → all were skipped (already handled)")
        return True

    def _check_existing_evr_pos(self, product, bom_id):
        """Check if POs already exist for this product from EVR flows"""
        bom = self.env['mrp.bom'].browse(bom_id)
        if not bom.exists():
            return False

        # Get BOM product info for origin matching
        product_code = bom.product_id.default_code or bom.product_tmpl_id.default_code or ''
        product_name = bom.product_id.name or bom.product_tmpl_id.name or ''

        # Check for customer POs (CFE)
        customer_pos = self.env['purchase.order'].search([
            ('origin', 'like', f'EVR-Manufacture - [{product_code}] {product_name}'),
            ('order_line.product_id', '=', product.id),
            ('state', 'in', ['draft', 'sent', 'to approve', 'purchase'])
        ])

        # Check for vendor POs
        # vendor_pos = self.env['purchase.order'].search([
        #     ('origin', 'like', f'BOM [{product_code}] {product_name}'),
        #     ('order_line.product_id', '=', product.id),
        #     ('state', 'in', ['draft', 'sent', 'to approve', 'purchase'])
        # ])
        vendor_pos = self.env['purchase.order'].search([
            ('order_line.product_id', '=', product.id),
            ('state', 'in', ['draft', 'sent', 'to approve', 'purchase']),
            '|',  # OR condition
            ('origin', 'like', f'BOM [{product_code}] {product_name}'),
            ('origin', 'like', f'Vendor-Instant - {product_name}'),
        ])

        # return customer_pos or vendor_pos

        return vendor_pos


