# models/mrp_production.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # def create(self, vals):
    #     print("🔵 [create] vals:", vals)
    #     production = super().create(vals)
    #     print("🟢 [create] Created Production:", production.id, production.name)
    #
    #     if self.env.context.get('create_case2_pos'):
    #         print("⚡ Context has 'create_case2_pos'")
    #         if production.bom_id and production.bom_id.is_evr:
    #             print("✅ BOM is EVR, calling create_manufacture_pos()")
    #             production.create_manufacture_pos()
    #         else:
    #             print("❌ BOM missing or not EVR")
    #     else:
    #         print("⏩ Context does not have 'create_case2_pos'")
    #
    #     return production

    @api.model
    def create(self, vals):
        print("🔵 [create] vals:", vals)
        production = super().create(vals)
        print("🟢 [create] Created Production:", production.id, production.name)

        # Reset context values if this MO was created from EVR BOM
        if production.bom_id and production.bom_id.is_evr:
            print("✅ EVR BOM detected, resetting context values")
            self.env['mrp.bom.context'].reset_context_values(production.bom_id.id, production.id)

        if self.env.context.get('create_case2_pos'):
            print("⚡ Context has 'create_case2_pos'")
            if production.bom_id and production.bom_id.is_evr:
                print("✅ BOM is EVR, calling create_manufacture_pos()")
                production.create_manufacture_pos()
            else:
                print("❌ BOM missing or not EVR")
        else:
            print("⏩ Context does not have 'create_case2_pos'")

        return production

    def create_manufacture_pos(self):
        """Create POs when Manufacture button is clicked (Case 2) - Updated for context model"""
        print("🔵 [create_manufacture_pos] Called for MO:", self.id, self.name)

        if not self.bom_id or not self.bom_id.is_evr:
            print("❌ No BOM or BOM is not EVR -> Skipping")
            return

        # Get root BOM ID
        root_bom_id = self.bom_id.id

        project_partner = None
        if hasattr(self, 'project_id') and self.project_id:
            project_partner = self.project_id.partner_id
            print("🟢 Project Partner found:", project_partner.id, project_partner.name)
        else:
            raise ValidationError(
                f"⚠️ Manufacture Order {self.name} has no project or no customer linked. "
                f"Set a Project with a customer before creating POs."
            )

        customer_po_lines = []
        vendor_po_data = {}

        for move in self.move_raw_ids:
            bom_line = move.bom_line_id
            print("➡️ Processing Move:", move.id, move.product_id.name)

            if not bom_line:
                print("⏩ Skipping move, no BOM line")
                continue

            # Get context data instead of BOM line fields
            context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, bom_line.id)

            print(f"   Context Data (LLI={context_data['lli']}, "
                  f"A1={context_data['approval_1']}, A2={context_data['approval_2']}, "
                  f"CFE Qty={context_data['cfe_quantity']})")

            # Only process Case 2: LLI=False, Approval1=True, Approval2=True
            if (not context_data['lli'] and
                    context_data['approval_1'] and
                    context_data['approval_2'] and
                    context_data['cfe_quantity']):

                try:
                    cfe_qty = float(context_data['cfe_quantity'])
                except (ValueError, TypeError):
                    print("❌ Invalid CFE Quantity")
                    continue

                if cfe_qty <= 0:
                    print("❌ CFE Quantity <= 0, skipping")
                    continue

                required_qty = move.product_uom_qty
                remaining_qty = required_qty - cfe_qty

                print(f"   ✅ Case 2 Match -> Required: {required_qty}, "
                      f"CFE Qty: {cfe_qty}, Remaining: {remaining_qty}")

                # Customer PO line
                if not project_partner:
                    raise ValidationError(
                        f"⚠️ No customer found for Project in MO {self.name}. "
                        f"Cannot create Customer PO for product {move.product_id.display_name}."
                    )

                line_vals = {
                    'product_id': move.product_id.id,
                    'product_qty': cfe_qty,
                    'product_uom': move.product_id.uom_po_id.id,
                    'price_unit': 0.0,
                    'date_planned': fields.Datetime.now(),
                    'name': f"CFE - {move.product_id.name}",
                }
                customer_po_lines.append((0, 0, line_vals))
                print("   🟢 Added Customer PO line:", line_vals)

                # Vendor PO lines
                if remaining_qty > 0:
                    vendor = move.product_id._select_seller()
                    if not vendor:
                        raise ValidationError(
                            f"⚠️ No vendor found for product '{move.product_id.display_name}' "
                            f"in MO {self.name}. Please configure a vendor in product supplier info."
                        )

                    vendor_id = vendor.partner_id.id
                    if vendor_id not in vendor_po_data:
                        vendor_po_data[vendor_id] = {
                            'partner_id': vendor_id,
                            'origin': f"MO - {self.name}",
                            'order_line': []
                        }
                        print("   🆕 Vendor found, creating PO dict for:", vendor_id)

                    vendor_line_vals = {
                        'product_id': move.product_id.id,
                        'product_qty': remaining_qty,
                        'product_uom': move.product_id.uom_po_id.id,
                        'price_unit': vendor.price if vendor else 0.0,
                        'date_planned': fields.Datetime.now(),
                        'name': f"Vendor - {move.product_id.name}",
                    }
                    vendor_po_data[vendor_id]['order_line'].append((0, 0, vendor_line_vals))
                    print("   🟢 Added Vendor PO line:", vendor_line_vals)

        # Create customer PO
        if customer_po_lines and project_partner:
            customer_po_vals = {
                'partner_id': project_partner.id,
                'origin': f"CFE-Manufacture - {self.name}",
                'state': 'draft',
                'order_line': customer_po_lines,
            }
            self.env['purchase.order'].create(customer_po_vals)
            print("🟢 Customer PO Created:", customer_po_vals)
        else:
            print("⏩ No Customer PO created")

        # Create vendor POs
        for vendor_data in vendor_po_data.values():
            if vendor_data['order_line']:
                vendor_data['state'] = 'draft'
                self.env['purchase.order'].create(vendor_data)
                print("🟢 Vendor PO Created:", vendor_data)
            else:
                print("⏩ Vendor PO has no lines, skipped")

    # @api.model
    # def action_validate_and_create_mo(self, bom_id):
    #     print("🟢 [action_validate_and_create_mo] called with bom_id:", bom_id)
    #
    #     bom = self.env["mrp.bom"].browse(bom_id)
    #     print("🔎 BOM record:", bom, "is_evr:", bom.is_evr)
    #
    #     if not bom or not bom.is_evr:
    #         print("❌ Invalid BOM or not EVR")
    #         raise ValidationError("❌ Invalid or non-EVR BOM.")
    #
    #     project = bom.project_id if hasattr(bom, "project_id") else None
    #     print("🔎 Project found:", project)
    #
    #     if not project or not project.partner_id:
    #         print("❌ Project missing or partner not set")
    #         raise ValidationError("⚠️ Project and Customer must be set before Manufacture.")
    #
    #     # Use root BOM ID for context data
    #     root_bom_id = bom.id
    #     customer_po_lines = []
    #     vendor_po_data = {}
    #     print("🟢 Starting BOM line loop...")
    #
    #     for line in bom.bom_line_ids:
    #         # Get context data instead of BOM line fields
    #         context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, line.id)
    #
    #         print(f"➡️ Processing line {line.id} - {line.product_id.display_name}, "
    #               f"Context LLI={context_data['lli']}, A1={context_data['approval_1']}, "
    #               f"A2={context_data['approval_2']}, CFE={context_data['cfe_quantity']}")
    #
    #         if not (context_data['approval_1'] and context_data['approval_2']):
    #             print("⏩ Skipping line, approvals not satisfied in context")
    #             continue
    #
    #         required_qty = line.product_qty
    #         cfe_qty = float(context_data['cfe_quantity'] or 0)
    #         remaining_qty = required_qty - cfe_qty
    #         print(f"   Required={required_qty}, CFE={cfe_qty}, Remaining={remaining_qty}")
    #
    #         # Case 4: LLI False + approvals True (from context)
    #         if not context_data['lli'] and context_data['approval_1'] and context_data['approval_2']:
    #             print("✅ Case 4 matched")
    #
    #             # Customer PO
    #             if cfe_qty > 0:
    #                 line_vals = {
    #                     "product_id": line.product_id.id,
    #                     "product_qty": cfe_qty,
    #                     "product_uom": line.product_id.uom_po_id.id,
    #                     "price_unit": 0.0,
    #                     "date_planned": fields.Datetime.now(),
    #                     "name": f"CFE - {line.product_id.display_name}",
    #                 }
    #                 customer_po_lines.append((0, 0, line_vals))
    #                 print("🟢 Added Customer PO line:", line_vals)
    #
    #             # Vendor PO
    #             if remaining_qty > 0:
    #                 print("🔎 Vendor PO required, checking vendor...")
    #                 vendor = line.product_id._select_seller()
    #                 print("   Vendor found:", vendor)
    #
    #                 if not vendor:
    #                     print("❌ No vendor configured for product", line.product_id.display_name)
    #                     raise ValidationError(
    #                         f"⚠️ No vendor found for product '{line.product_id.display_name}'. "
    #                         f"Please configure a vendor."
    #                     )
    #
    #                 vid = vendor.partner_id.id
    #                 if vid not in vendor_po_data:
    #                     vendor_po_data[vid] = {
    #                         "partner_id": vid,
    #                         "origin": f"BOM {bom.display_name}",
    #                         "order_line": []
    #                     }
    #                     print("🆕 Created new Vendor PO dict for:", vendor.partner_id.name)
    #
    #                 vendor_line_vals = {
    #                     "product_id": line.product_id.id,
    #                     "product_qty": remaining_qty,
    #                     "product_uom": line.product_id.uom_po_id.id,
    #                     "price_unit": vendor.price or 0.0,
    #                     "date_planned": fields.Datetime.now(),
    #                     "name": f"Vendor - {line.product_id.display_name}",
    #                 }
    #                 vendor_po_data[vid]["order_line"].append((0, 0, vendor_line_vals))
    #                 print("🟢 Added Vendor PO line:", vendor_line_vals)
    #
    #     print("✅ Finished BOM line loop")
    #
    #     # Create customer PO
    #     if customer_po_lines:
    #         customer_po_vals = {
    #             "partner_id": project.partner_id.id,
    #             "origin": f"EVR-Manufacture - {bom.display_name}",
    #             "order_line": customer_po_lines,
    #         }
    #         self.env["purchase.order"].create(customer_po_vals)
    #         print("🟢 Customer PO Created:", customer_po_vals)
    #     else:
    #         print("⏩ No Customer PO to create")
    #
    #     # Create vendor POs
    #     for vdata in vendor_po_data.values():
    #         self.env["purchase.order"].create(vdata)
    #         print("🟢 Vendor PO Created:", vdata)
    #
    #     # Finally create MO
    #     action = {
    #         "res_model": "mrp.production",
    #         "name": "Manufacture Orders",
    #         "type": "ir.actions.act_window",
    #         "views": [[False, "form"]],
    #         "target": "current",
    #         "context": {"default_bom_id": bom.id},
    #     }
    #     print("🟢 Returning Manufacture action:", action)
    #     return action

    # without main vendor
    # @api.model
    # def action_validate_and_create_mo(self, bom_id):
    #     print("🟢 [action_validate_and_create_mo] called with bom_id:", bom_id)
    #
    #     bom = self.env["mrp.bom"].browse(bom_id)
    #     print("🔎 BOM record:", bom, "is_evr:", bom.is_evr)
    #
    #     if not bom or not bom.is_evr:
    #         print("❌ Invalid BOM or not EVR")
    #         raise ValidationError("❌ Invalid or non-EVR BOM.")
    #
    #     project = bom.project_id if hasattr(bom, "project_id") else None
    #     print("🔎 Project found:", project)
    #
    #     if not project or not project.partner_id:
    #         print("❌ Project missing or partner not set")
    #         raise ValidationError("⚠️ Project and Customer must be set before Manufacture.")
    #
    #     # Use root BOM ID for context data
    #     root_bom_id = bom.id
    #     print("🟢 Starting BOM line loop...")
    #
    #     for line in bom.bom_line_ids:
    #         # Get context data instead of BOM line fields
    #         context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, line.id)
    #
    #         print(f"➡️ Processing line {line.id} - {line.product_id.display_name}, "
    #               f"Context LLI={context_data['lli']}, A1={context_data['approval_1']}, "
    #               f"A2={context_data['approval_2']}, CFE={context_data['cfe_quantity']}")
    #
    #         if not (context_data['approval_1'] and context_data['approval_2']):
    #             print("⏩ Skipping line, approvals not satisfied in context")
    #             continue
    #
    #         required_qty = line.product_qty
    #         cfe_qty = float(context_data['cfe_quantity'] or 0)
    #         remaining_qty = required_qty - cfe_qty
    #         print(f"   Required={required_qty}, CFE={cfe_qty}, Remaining={remaining_qty}")
    #
    #         # Case 4: LLI False + approvals True (from context)
    #         if not context_data['lli'] and context_data['approval_1'] and context_data['approval_2']:
    #             print("✅ Case 4 matched")
    #
    #             # Customer PO -> Create immediately per line
    #             if cfe_qty > 0:
    #                 customer_po_vals = {
    #                     "partner_id": project.partner_id.id,
    #                     "origin": f"EVR-Manufacture - {bom.display_name}",
    #                     "order_line": [(0, 0, {
    #                         "product_id": line.product_id.id,
    #                         "product_qty": cfe_qty,
    #                         "product_uom": line.product_id.uom_po_id.id,
    #                         "price_unit": 0.0,
    #                         "date_planned": fields.Datetime.now(),
    #                         "name": f"CFE - {line.product_id.display_name}",
    #                     })],
    #                 }
    #                 self.env["purchase.order"].create(customer_po_vals)
    #                 print("🟢 Customer PO Created (per line):", customer_po_vals)
    #
    #             # Vendor PO -> Create immediately per line
    #             if remaining_qty > 0:
    #                 print("🔎 Vendor PO required, checking vendor...")
    #                 vendor = line.product_id._select_seller()
    #                 print("   Vendor found:", vendor)
    #
    #                 if not vendor:
    #                     print("❌ No vendor configured for product", line.product_id.display_name)
    #                     raise ValidationError(
    #                         f"⚠️ No vendor found for product '{line.product_id.display_name}'. "
    #                         f"Please configure a vendor."
    #                     )
    #
    #                 vendor_po_vals = {
    #                     "partner_id": vendor.partner_id.id,
    #                     "origin": f"BOM {bom.display_name}",
    #                     "order_line": [(0, 0, {
    #                         "product_id": line.product_id.id,
    #                         "product_qty": remaining_qty,
    #                         "product_uom": line.product_id.uom_po_id.id,
    #                         "price_unit": vendor.price or 0.0,
    #                         "date_planned": fields.Datetime.now(),
    #                         "name": f"Vendor - {line.product_id.display_name}",
    #                     })],
    #                 }
    #                 self.env["purchase.order"].create(vendor_po_vals)
    #                 print("🟢 Vendor PO Created (per line):", vendor_po_vals)
    #
    #     print("✅ Finished BOM line loop")
    #
    #     # Finally create MO
    #     action = {
    #         "res_model": "mrp.production",
    #         "name": "Manufacture Orders",
    #         "type": "ir.actions.act_window",
    #         "views": [[False, "form"]],
    #         "target": "current",
    #         "context": {"default_bom_id": bom.id},
    #     }
    #     print("🟢 Returning Manufacture action:", action)
    #     return action

    # @api.model
    # def action_validate_and_create_mo(self, bom_id):
    #     print("🟢 [action_validate_and_create_mo] called with bom_id:", bom_id)
    #
    #     bom = self.env["mrp.bom"].browse(bom_id)
    #     print("🔎 BOM record:", bom, "is_evr:", bom.is_evr)
    #
    #     if not bom or not bom.is_evr:
    #         print("❌ Invalid BOM or not EVR")
    #         raise ValidationError("❌ Invalid or non-EVR BOM.")
    #
    #     project = bom.project_id if hasattr(bom, "project_id") else None
    #     print("🔎 Project found:", project)
    #
    #     if not project or not project.partner_id:
    #         print("❌ Project missing or partner not set")
    #         raise ValidationError("⚠️ Project and Customer must be set before Manufacture.")
    #
    #     # Use root BOM ID for context data
    #     root_bom_id = bom.id
    #     print("🟢 Starting BOM line loop...")
    #
    #     for line in bom.bom_line_ids:
    #         # Get context data instead of BOM line fields
    #         context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, line.id)
    #
    #         print(f"➡️ Processing line {line.id} - {line.product_id.display_name}, "
    #               f"Context LLI={context_data['lli']}, A1={context_data['approval_1']}, "
    #               f"A2={context_data['approval_2']}, CFE={context_data['cfe_quantity']}")
    #
    #         if not (context_data['approval_1'] and context_data['approval_2']):
    #             print("⏩ Skipping line, approvals not satisfied in context")
    #             continue
    #
    #         required_qty = line.product_qty
    #         cfe_qty = float(context_data['cfe_quantity'] or 0)
    #         remaining_qty = required_qty - cfe_qty
    #         print(f"   Required={required_qty}, CFE={cfe_qty}, Remaining={remaining_qty}")
    #
    #         # Case 4: LLI False + approvals True (from context)
    #         if not context_data['lli'] and context_data['approval_1'] and context_data['approval_2']:
    #             print("✅ Case 4 matched")
    #
    #             # Customer PO -> Create immediately per line
    #             if cfe_qty > 0:
    #                 customer_po_vals = {
    #                     "partner_id": project.partner_id.id,
    #                     "origin": f"EVR-Manufacture - {bom.display_name}",
    #                     "order_line": [(0, 0, {
    #                         "product_id": line.product_id.id,
    #                         "product_qty": cfe_qty,
    #                         "product_uom": line.product_id.uom_po_id.id,
    #                         "price_unit": 0.0,
    #                         "date_planned": fields.Datetime.now(),
    #                         "name": f"CFE - {line.product_id.display_name}",
    #                     })],
    #                 }
    #                 self.env["purchase.order"].create(customer_po_vals)
    #                 print("🟢 Customer PO Created (per line):", customer_po_vals)
    #
    #             # Vendor PO -> Create immediately per line
    #             # Vendor PO -> Create immediately per line
    #             if remaining_qty > 0:
    #                 print("🔎 Vendor PO required, checking vendor...")
    #
    #                 # Look for main vendor first
    #                 main_vendor = line.product_id.seller_ids.filtered(lambda s: s.main_vendor)
    #                 vendor = main_vendor[0] if main_vendor else line.product_id._select_seller()
    #
    #                 print("   Vendor found:", vendor)
    #
    #                 if not vendor:
    #                     print("❌ No vendor configured for product", line.product_id.display_name)
    #                     raise ValidationError(
    #                         f"⚠️ No vendor found for product '{line.product_id.display_name}'. "
    #                         f"Please configure a vendor."
    #                     )
    #
    #                 vendor_po_vals = {
    #                     "partner_id": vendor.partner_id.id,
    #                     "origin": f"BOM {bom.display_name}",
    #                     "order_line": [(0, 0, {
    #                         "product_id": line.product_id.id,
    #                         "product_qty": remaining_qty,
    #                         "product_uom": line.product_id.uom_po_id.id,
    #                         "price_unit": vendor.price or line.product_id.list_price,
    #                         "date_planned": fields.Datetime.now(),
    #                         "name": f"Vendor - {line.product_id.display_name}",
    #                     })],
    #                 }
    #                 self.env["purchase.order"].create(vendor_po_vals)
    #                 print("🟢 Vendor PO Created (per line):", vendor_po_vals)
    #                 self.env['mrp.bom.context'].mark_pos_created_for_bom(bom_id)
    #
    #     print("✅ Finished BOM line loop")
    #
    #     # Finally create MO
    #     action = {
    #         "res_model": "mrp.production",
    #         "name": "Manufacture Orders",
    #         "type": "ir.actions.act_window",
    #         "views": [[False, "form"]],
    #         "target": "current",
    #         "context": {"default_bom_id": bom.id},
    #     }
    #     print("🟢 Returning Manufacture action:", action)
    #     return action

    @api.model
    def action_validate_and_create_mo(self, bom_id):
        print("🟢 [action_validate_and_create_mo] called with bom_id:", bom_id)

        bom = self.env["mrp.bom"].browse(bom_id)
        print("🔎 BOM record:", bom, "is_evr:", bom.is_evr)

        if not bom or not bom.is_evr:
            print("❌ Invalid BOM or not EVR")
            raise ValidationError("❌ Invalid or non-EVR BOM.")

        project = bom.project_id if hasattr(bom, "project_id") else None
        print("🔎 Project found:", project)

        if not project or not project.partner_id:
            print("❌ Project missing or partner not set")
            raise ValidationError("⚠️ Project and Customer must be set before Manufacture.")

        # Use root BOM ID for context data
        root_bom_id = bom.id
        print("🟢 Starting BOM line loop...")

        # 🔹 Get mo_internal_ref from BOM (or fallback from context later if you want)
        mo_internal_ref = getattr(bom, "mo_internal_ref", False)
        print("📌 mo_internal_ref:", mo_internal_ref)

        for line in bom.bom_line_ids:
            # Get context data instead of BOM line fields
            context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, line.id)

            print(f"➡️ Processing line {line.id} - {line.product_id.display_name}, "
                  f"Context LLI={context_data['lli']}, A1={context_data['approval_1']}, "
                  f"A2={context_data['approval_2']}, CFE={context_data['cfe_quantity']}")

            if not (context_data['approval_1'] and context_data['approval_2']):
                print("⏩ Skipping line, approvals not satisfied in context")
                continue

            required_qty = line.product_qty
            cfe_qty = float(context_data['cfe_quantity'] or 0)
            remaining_qty = required_qty - cfe_qty
            print(f"   Required={required_qty}, CFE={cfe_qty}, Remaining={remaining_qty}")

            # Case 4: LLI False + approvals True (from context)
            if not context_data['lli'] and context_data['approval_1'] and context_data['approval_2']:
                print("✅ Case 4 matched")

                # --------------------------
                # Customer PO -> per line
                # --------------------------
                if cfe_qty > 0:
                    customer_po_vals = {
                        "partner_id": project.partner_id.id,
                        "origin": f"EVR-Manufacture - {bom.display_name}",
                        "order_line": [(0, 0, {
                            "product_id": line.product_id.id,
                            "product_qty": cfe_qty,
                            "product_uom": line.product_id.uom_po_id.id,
                            "price_unit": 0.0,
                            "date_planned": fields.Datetime.now(),
                            "name": f"CFE - {line.product_id.display_name}",
                        })],
                    }
                    # 🔹 Add mo_internal_ref if available
                    if mo_internal_ref:
                        customer_po_vals["mo_internal_ref"] = mo_internal_ref

                    self.env["purchase.order"].create(customer_po_vals)
                    print("🟢 Customer PO Created (per line):", customer_po_vals)

                # --------------------------
                # Vendor PO -> per line
                # --------------------------
                if remaining_qty > 0:
                    print("🔎 Vendor PO required, checking vendor...")

                    # Look for main vendor first
                    main_vendor = line.product_id.seller_ids.filtered(lambda s: s.main_vendor)
                    vendor = main_vendor[0] if main_vendor else line.product_id._select_seller()

                    print("   Vendor found:", vendor)

                    if not vendor:
                        print("❌ No vendor configured for product", line.product_id.display_name)
                        raise ValidationError(
                            f"⚠️ No vendor found for product '{line.product_id.display_name}'. "
                            f"Please configure a vendor."
                        )

                    vendor_po_vals = {
                        "partner_id": vendor.partner_id.id,
                        "origin": f"BOM {bom.display_name}",
                        "order_line": [(0, 0, {
                            "product_id": line.product_id.id,
                            "product_qty": remaining_qty,
                            "product_uom": line.product_id.uom_po_id.id,
                            "price_unit": vendor.price or line.product_id.list_price,
                            "date_planned": fields.Datetime.now(),
                            "name": f"Vendor - {line.product_id.display_name}",
                        })],
                    }
                    # 🔹 Add mo_internal_ref if available
                    if mo_internal_ref:
                        vendor_po_vals["mo_internal_ref"] = mo_internal_ref

                    self.env["purchase.order"].create(vendor_po_vals)
                    print("🟢 Vendor PO Created (per line):", vendor_po_vals)
                    self.env['mrp.bom.context'].mark_pos_created_for_bom(bom_id)

        print("✅ Finished BOM line loop")

        # Finally create MO
        action = {
            "res_model": "mrp.production",
            "name": "Manufacture Orders",
            "type": "ir.actions.act_window",
            "views": [[False, "form"]],
            "target": "current",
            "context": {"default_bom_id": bom.id},
        }
        print("🟢 Returning Manufacture action:", action)
        return action
