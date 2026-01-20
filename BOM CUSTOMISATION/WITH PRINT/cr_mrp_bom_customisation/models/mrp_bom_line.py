# models/mrp_bom_line.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    cfe_quantity = fields.Char(
        string='CFE Quantity',
        help="Customer Furnished Equipment quantity - supplied by customer at zero cost"
    )
    lli = fields.Boolean(string='LLI', default=False)
    approval_1 = fields.Boolean(string='Approval 1', default=False)
    approval_2 = fields.Boolean(string='Approval 2', default=False)
    po_created = fields.Boolean(string='PO Created', default=False)
    mo_internal_ref = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Preferred Manufacturer",
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
        help="Select the manufacturer/vendor defined on the product card."
    )


    @api.depends('bom_id.is_evr')
    def _compute_show_cfe_quantity(self):
        """Compute whether CFE quantity and new fields should be shown"""
        for line in self:
            show = line.bom_id.is_evr
            line.show_cfe_quantity = show
            line.show_lli = show
            line.show_approval_1 = show
            line.show_approval_2 = show
            line.show_mo_internal_ref = show

    show_cfe_quantity = fields.Boolean(
        string='Show CFE Quantity',
        compute='_compute_show_cfe_quantity',
        store=True,
        help="Technical field to control CFE quantity visibility"
    )
    show_lli = fields.Boolean(compute='_compute_show_cfe_quantity', store=True)
    show_approval_1 = fields.Boolean(compute='_compute_show_cfe_quantity', store=True)
    show_approval_2 = fields.Boolean(compute='_compute_show_cfe_quantity', store=True)
    show_mo_internal_ref = fields.Boolean(compute='_compute_show_cfe_quantity', store=True)


    # def _create_instant_pos_with_context(self, root_bom_id, bom_line):
    #     """Create both customer and vendor POs instantly using context data"""
    #     pos = []
    #     context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, bom_line.id)
    #     cfe_qty = float(context_data['cfe_quantity'] or '0')
    #
    #     print("🔵 [_create_instant_pos_with_context] Creating Instant POs for qty:", cfe_qty)
    #
    #     # Get root BOM for project partner and origin formatting
    #     root_bom = self.env['mrp.bom'].browse(root_bom_id)
    #     project_partner = root_bom.project_id.partner_id if root_bom.project_id else None
    #
    #     if not project_partner:
    #         raise ValidationError("⚠️ Project not set on root BOM or missing project partner.")
    #
    #     # Get product codes for proper origin formatting
    #     product_code = root_bom.product_id.default_code or root_bom.product_tmpl_id.default_code or ''
    #     product_name = root_bom.product_id.name or root_bom.product_tmpl_id.name or ''
    #     cfe_project_location_id = bom_line.bom_id.cfe_project_location_id
    #     # Customer PO with proper origin
    #     customer_po_vals = {
    #         'partner_id': project_partner.id,
    #         'cfe_project_location_id':cfe_project_location_id.id,
    #         'origin': f"EVR-Manufacture - [{product_code}] {product_name}",
    #         'state': 'draft',
    #         'order_line': [(0, 0, {
    #             'product_id': bom_line.product_id.id,
    #             'product_qty': cfe_qty,
    #             'product_uom': bom_line.product_id.uom_po_id.id,
    #             'price_unit': 0.0,
    #             'date_planned': fields.Datetime.now(),
    #             'name': f"CFE - {bom_line.product_id.display_name}",
    #         })]
    #     }
    #     po = self.env['purchase.order'].create(customer_po_vals)
    #     pos.append(po.id)
    #     print("🟢 Customer Instant PO Created:", po.id, po.name)
    #
    #     # Vendor PO
    #     required_qty = bom_line.product_qty
    #     remaining_qty = required_qty - cfe_qty
    #
    #     if remaining_qty > 0:
    #         print("🔎 Vendor PO required, checking vendor...")
    #
    #         vendor_partner_id = context_data.get("mo_internal_ref")  # 👈 new field from context
    #         vendor = False
    #
    #         if vendor_partner_id:
    #             # Ensure it's still a valid vendor for this product
    #             seller = bom_line.product_id.seller_ids.filtered(lambda s: s.partner_id.id == vendor_partner_id)
    #             if seller:
    #                 vendor = seller[0]
    #                 print(f"   ✅ Using selected vendor from context: {vendor.display_name}")
    #             else:
    #                 print("   ⚠️ Selected vendor not valid anymore for this product, falling back...")
    #
    #         # Fallback if no valid context vendor
    #         if not vendor:
    #             main_vendor = bom_line.product_id.seller_ids.filtered(lambda s: s.main_vendor)
    #             vendor = main_vendor[0] if main_vendor else bom_line.product_id._select_seller()
    #             print(f"   🔄 Fallback vendor used: {vendor.partner_id.display_name if vendor else 'None'}")
    #
    #         if not vendor:
    #             raise ValidationError(f"⚠️ No vendor found for product '{bom_line.product_id.display_name}'.")
    #
    #         vendor_po_vals = {
    #             'partner_id': vendor.partner_id.id,
    #             'origin': f"BOM [{product_code}] {product_name}",  # Updated origin format
    #             'state': 'draft',
    #             'cfe_project_location_id': cfe_project_location_id.id,
    #             'order_line': [(0, 0, {
    #                 'product_id': bom_line.product_id.id,
    #                 'product_qty': remaining_qty,
    #                 'product_uom': bom_line.product_id.uom_po_id.id,
    #                 'price_unit': vendor.price or 0.0,
    #                 'date_planned': fields.Datetime.now(),
    #                 'name': f"Vendor - {bom_line.product_id.display_name}",
    #             })]
    #         }
    #         vpo = self.env['purchase.order'].create(vendor_po_vals)
    #         pos.append(vpo.id)
    #         self.env['mrp.bom.context'].mark_pos_created_for_bom(bom_line.bom_id.id)
    #         print("🟢 Vendor Instant PO Created:", vpo.id, vpo.name)
    #
    #         # Mark PO as created in context - keep this True to prevent MTO duplicates
    #         self.env['mrp.bom.context'].set_context_data(
    #             root_bom_id, bom_line.id, bom_line.product_id.id, 'po_created', True
    #         )

    def _create_instant_pos_with_context(self, root_bom_id, bom_line):
        """Create both customer and vendor POs instantly using context data"""
        result = {
            "customer_po": False,
            "vendor_po": False,
            "customer_po_id": False,
            "vendor_po_id": False,
        }
        pos = []
        context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, bom_line.id)
        cfe_qty = float(context_data['cfe_quantity'] or '0')

        print("🔵 [_create_instant_pos_with_context] Creating Instant POs for qty:", cfe_qty)

        # --- Customer PO ---
        root_bom = self.env['mrp.bom'].browse(root_bom_id)
        project_partner = root_bom.project_id.partner_id if root_bom.project_id else None

        if not project_partner:
            raise ValidationError("⚠️ Project not set on root BOM or missing project partner.")

        product_code = root_bom.product_id.default_code or root_bom.product_tmpl_id.default_code or ''
        product_name = root_bom.product_id.name or root_bom.product_tmpl_id.name or ''
        cfe_project_location_id = bom_line.bom_id.cfe_project_location_id

        customer_po_vals = {
            'partner_id': project_partner.id,
            'cfe_project_location_id': cfe_project_location_id.id,
            'origin': f"EVR-Manufacture - [{product_code}] {product_name}",
            'state': 'draft',
            'order_line': [(0, 0, {
                'product_id': bom_line.product_id.id,
                'product_qty': cfe_qty,
                'product_uom': bom_line.product_id.uom_po_id.id,
                'price_unit': 0.0,
                'date_planned': fields.Datetime.now(),
                'name': f"CFE - {bom_line.product_id.display_name}",
            })]
        }
        po = self.env['purchase.order'].create(customer_po_vals)
        pos.append(po.id)
        print("🟢 Customer Instant PO Created:", po.id, po.name)

        result["customer_po"] = True
        result["customer_po_id"] = po.id

        # --- Vendor PO ---
        required_qty = bom_line.product_qty
        print('bom_line.product_id.name : ',bom_line.product_id.name)
        print('required_qty :  ',required_qty)
        remaining_qty = required_qty - cfe_qty
        print('remaining_qty :  ', remaining_qty)

        if remaining_qty > 0:
            vendor_partner_id = context_data.get("mo_internal_ref")
            vendor = False

            if vendor_partner_id:
                seller = bom_line.product_id.seller_ids.filtered(lambda s: s.partner_id.id == vendor_partner_id)
                if seller:
                    vendor = seller[0]
                    print(f"   ✅ Using selected vendor from context: {vendor.display_name}")

            if not vendor:
                main_vendor = bom_line.product_id.seller_ids.filtered(lambda s: s.main_vendor)
                vendor = main_vendor[0] if main_vendor else bom_line.product_id._select_seller()

            if vendor:
                vendor_po_vals = {
                    'partner_id': vendor.partner_id.id,
                    'origin': f"BOM [{product_code}] {product_name}",
                    'state': 'draft',
                    'cfe_project_location_id': cfe_project_location_id.id,
                    'order_line': [(0, 0, {
                        'product_id': bom_line.product_id.id,
                        'product_qty': remaining_qty,
                        'product_uom': bom_line.product_id.uom_po_id.id,
                        'price_unit': vendor.price or bom_line.product_id.list_price,
                        'date_planned': fields.Datetime.now(),
                        'name': f"Vendor - {bom_line.product_id.display_name}",
                    })]
                }
                vpo = self.env['purchase.order'].create(vendor_po_vals)
                pos.append(vpo.id)
                print("🟢 Vendor Instant PO Created:", vpo.id, vpo.name)

                result["vendor_po"] = True
                result["vendor_po_id"] = vpo.id
            else:
                print("⚠️ Vendor not created, no vendor found")
                result["vendor_po"] = False

            self.env['mrp.bom.context'].set_context_data(
                root_bom_id, bom_line.id, bom_line.product_id.id, 'po_created', True
            )
        return result

    # Also update the validation method to not reset po_created after instant PO creation
    # def validate_third_boolean(self, vals):
    #     """
    #     Check rules before allowing the 3rd boolean to be ticked.
    #     Now uses context data for validation.
    #     """
    #     root_bom_id = self.env.context.get('root_bom_id') or self.bom_id.id
    #
    #     for line in self:
    #         # Get context data for validation
    #         context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, line.id)
    #
    #         lli = vals.get("lli", context_data['lli'])
    #         a1 = vals.get("approval_1", context_data['approval_1'])
    #         a2 = vals.get("approval_2", context_data['approval_2'])
    #         cfe_quantity = vals.get("cfe_quantity", context_data['cfe_quantity'])
    #
    #         print(f"🔎 [validate_third_boolean] BOM Line {line.id} - Root BOM: {root_bom_id}")
    #         print(f"   Context Data -> LLI={lli}, A1={a1}, A2={a2}, CFE={cfe_quantity}")
    #
    #         # Only if all three would become True
    #         if lli and a1 and a2:
    #             print("✅ All three flags would be TRUE → checking rules...")
    #
    #             # # Check if PO already created for this context
    #             # if context_data.get('po_created'):
    #             #     print("⏩ PO already created for this context → allow")
    #             #     continue
    #
    #             if not cfe_quantity or float(cfe_quantity or 0) <= 0:
    #                 print("❌ CFE quantity missing or <= 0")
    #                 raise ValidationError("⚠️ CFE Quantity must be > 0 before enabling all 3 flags.")
    #
    #             # Get root BOM for project validation
    #             root_bom = self.env['mrp.bom'].browse(root_bom_id)
    #             if not root_bom.project_id or not root_bom.project_id.partner_id:
    #                 print("❌ Missing project partner on root BOM")
    #                 raise ValidationError("⚠️ Project Partner must be set on root BOM before enabling all 3 flags.")
    #
    #             # Vendor check
    #             main_vendor = line.product_id.seller_ids.filtered(lambda s: s.main_vendor)
    #             vendor = main_vendor[0] if main_vendor else line.product_id._select_seller()
    #             print(f"   🔎 Vendor found: {vendor.partner_id.name if vendor else 'None'}")
    #
    #             if not vendor:
    #                 print("❌ No vendor defined on product")
    #                 raise ValidationError(
    #                     f"⚠️ No vendor defined for {line.product_id.display_name}. Please configure at least one vendor."
    #                 )
    #
    #             # If validation passes, create POs immediately
    #             print("✅ Validation passed, creating instant POs...")
    #             self._create_instant_pos_with_context(root_bom_id, line)
    #             # Note: po_created is set to True inside _create_instant_pos_with_context
    #             # and should NOT be reset to prevent MTO duplicates
    #             print('yes instant pos done.....')
    #         else:
    #             print("⏩ Not all three flags are TRUE → no validation triggered")
    #
    #     return True

    def validate_third_boolean(self, vals):
        """
        Check rules before allowing the 3rd boolean to be ticked.
        Now uses context data for validation and returns PO result.
        """
        root_bom_id = self.env.context.get('root_bom_id') or self.bom_id.id
        results = []

        for line in self:
            # Get context data for validation
            context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, line.id)

            lli = vals.get("lli", context_data['lli'])
            a1 = vals.get("approval_1", context_data['approval_1'])
            a2 = vals.get("approval_2", context_data['approval_2'])
            cfe_quantity = vals.get("cfe_quantity", context_data['cfe_quantity'])

            print(f"🔎 [validate_third_boolean] BOM Line {line.id} - Root BOM: {root_bom_id}")
            print(f"   Context Data -> LLI={lli}, A1={a1}, A2={a2}, CFE={cfe_quantity}")

            # Only if all three would become True
            if lli and a1 and a2:
                print("✅ All three flags would be TRUE → checking rules...")

                if not cfe_quantity or float(cfe_quantity or 0) <= 0:
                    print("❌ CFE quantity missing or <= 0")
                    raise ValidationError("⚠️ CFE Quantity must be > 0 before enabling all 3 flags.")

                # Get root BOM for project validation
                root_bom = self.env['mrp.bom'].browse(root_bom_id)
                if not root_bom.project_id or not root_bom.project_id.partner_id:
                    print("❌ Missing project partner on root BOM")
                    raise ValidationError("⚠️ Project Partner must be set on root BOM before enabling all 3 flags.")

                # Vendor check
                main_vendor = line.product_id.seller_ids.filtered(lambda s: s.main_vendor)
                vendor = main_vendor[0] if main_vendor else line.product_id._select_seller()
                print(f"   🔎 Vendor found: {vendor.partner_id.name if vendor else 'None'}")

                if not vendor:
                    print("❌ No vendor defined on product")
                    raise ValidationError(
                        f"⚠️ No vendor defined for {line.product_id.display_name}. Please configure at least one vendor."
                    )

                # If validation passes, create POs immediately
                print("✅ Validation passed, creating instant POs...")
                po_result = self._create_instant_pos_with_context(root_bom_id, line)
                results.append({
                    "bom_line_id": line.id,
                    **po_result
                })
                print('yes instant pos done.....')
            else:
                print("⏩ Not all three flags are TRUE → no validation triggered")

        return results if results else True

