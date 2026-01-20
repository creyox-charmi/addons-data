# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields, api
from odoo.exceptions import ValidationError



class MrpProduction(models.Model):
    _inherit = 'mrp.production'



    @api.model
    def create(self, vals):
        production = super().create(vals)
        ctx = self.env.context

        # ✅ If POs exist in context, link them to this MO
        if ctx.get("pos"):
            po_ids = ctx["pos"]
            purchase_orders = self.env["purchase.order"].browse(po_ids)

            # Update each PO with this MO id (One2many ←→ Many2one)
            purchase_orders.write({"production_id": production.id})

        # Reset context values if this MO was created from EVR BOM
        if production.bom_id and production.bom_id.is_evr:
            self.env['mrp.bom.context'].reset_context_values(production.bom_id.id, production.id)

        return production

    def create_manufacture_pos(self):
        """Create POs when Manufacture button is clicked (Case 2) - Updated for context model"""

        if not self.bom_id or not self.bom_id.is_evr:
            return

        # Get root BOM ID
        root_bom_id = self.bom_id.id

        project_partner = None
        if hasattr(self, 'project_id') and self.project_id:
            project_partner = self.project_id.partner_id
        else:
            raise ValidationError(
                f"⚠️ Manufacture Order {self.name} has no project or no customer linked. "
                f"Set a Project with a customer before creating POs."
            )

        customer_po_lines = []
        vendor_po_data = {}

        for move in self.move_raw_ids:
            bom_line = move.bom_line_id

            if not bom_line:
                continue

            # Get context data instead of BOM line fields
            context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, bom_line.id)


            # Only process Case 2: LLI=False, Approval1=True, Approval2=True
            if (not context_data['lli'] and
                    context_data['approval_1'] and
                    context_data['approval_2'] and
                    context_data['cfe_quantity']):

                try:
                    cfe_qty = float(context_data['cfe_quantity'])
                except (ValueError, TypeError):
                    continue

                if cfe_qty <= 0:
                    continue

                required_qty = move.product_uom_qty
                remaining_qty = required_qty - cfe_qty


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

                    vendor_line_vals = {
                        'product_id': move.product_id.id,
                        'product_qty': remaining_qty,
                        'product_uom': move.product_id.uom_po_id.id,
                        'price_unit': vendor.price if vendor else 0.0,
                        'date_planned': fields.Datetime.now(),
                        'name': f"Vendor - {move.product_id.name}",
                    }
                    vendor_po_data[vendor_id]['order_line'].append((0, 0, vendor_line_vals))

        # Create customer PO
        if customer_po_lines and project_partner:
            customer_po_vals = {
                'partner_id': project_partner.id,
                'origin': f"CFE-Manufacture - {self.name}",
                'state': 'draft',
                'order_line': customer_po_lines,
            }
            self.env['purchase.order'].create(customer_po_vals)
        else:
            print("⏩ No Customer PO created")

        # Create vendor POs
        for vendor_data in vendor_po_data.values():
            if vendor_data['order_line']:
                vendor_data['state'] = 'draft'
                self.env['purchase.order'].create(vendor_data)
            else:
                print("⏩ Vendor PO has no lines, skipped")



    @api.model
    def action_validate_and_create_mo(self, bom_id):
        messages = []  # 🔹 Collect messages to send back to JS
        pos = []

        bom = self.env["mrp.bom"].browse(bom_id)
        if not bom or not bom.is_evr:
            msg = "❌ Invalid or non-EVR BOM."
            messages.append({"type": "danger", "msg": msg})
            raise ValidationError(msg)

        project = getattr(bom, "project_id", None)
        if not project or not project.partner_id:
            msg = "⚠️ Project and Customer must be set before Manufacture."
            messages.append({"type": "danger", "msg": msg})
            raise ValidationError(msg)

        root_bom_id = bom.id
        mo_internal_ref = getattr(bom, "mo_internal_ref", False)

        context = self.env['mrp.bom.context'].search([
            ('root_bom_id', '=', root_bom_id),
            ('is_active_session', '=', True),
            ('related_mo_id', '=', False)
        ])

        for data in context:
            if data.lli:
                continue

            if not (data.approval_1 and data.approval_2):
                continue

            required_qty = float(data.product_qty or 0)
            # required_qty = 1
            cfe_qty = float(data.cfe_quantity or 0)
            remaining_qty = required_qty - cfe_qty

            cfe_project_location_id = data.root_bom_id.cfe_project_location_id

            # ----------------- Customer PO -----------------
            if cfe_qty > 0:
                customer_po_vals = {
                    "partner_id": project.partner_id.id,
                    "origin": f"EVR-Manufacture - {bom.display_name}",
                    "cfe_project_location_id": cfe_project_location_id.id,
                    "order_line": [(0, 0, {
                        "product_id": data.product_id.id,
                        "product_qty": cfe_qty,
                        "product_uom": data.product_id.uom_po_id.id,
                        "price_unit": 0.0,
                        "date_planned": fields.Datetime.now(),
                        "name": f"CFE - {data.product_id.display_name}",
                    })],
                }
                if mo_internal_ref:
                    customer_po_vals["mo_internal_ref"] = mo_internal_ref

                cpo = self.env["purchase.order"].create(customer_po_vals)
                pos.append(cpo.id)
                messages.append({
                    "type": "success",
                    "msg": f"✅ Customer PO created for {data.product_id.display_name} ({cfe_qty})"
                })

            # ----------------- Vendor PO -----------------
            if remaining_qty > 0:
                vendor = (
                        data.product_id.seller_ids.filtered(lambda s: s.main_vendor)[:1]
                        or data.product_id._select_seller()
                )
                if not vendor:
                    messages.append({
                        "type": "warning",
                        "msg": f"⚠️ Vendor PO not created for {data.product_id.display_name} "
                               f"({remaining_qty}): No vendor configured on product."
                    })
                    continue

                if not vendor.partner_id:
                    messages.append({
                        "type": "warning",
                        "msg": f"⚠️ Vendor PO not created for {data.product_id.display_name} "
                               f"({remaining_qty}): Vendor record has no partner linked."
                    })
                    continue

                if not (vendor.price or data.product_id.list_price):
                    messages.append({
                        "type": "warning",
                        "msg": f"⚠️ Vendor PO not created for {data.product_id.display_name} "
                               f"({remaining_qty}): No vendor price or product list price found."
                    })
                    continue

                # ✅ All good → create vendor PO
                vendor_po_vals = {
                    "partner_id": vendor.partner_id.id,
                    "origin": f"BOM {bom.display_name}",
                    "cfe_project_location_id": cfe_project_location_id.id,
                    "order_line": [(0, 0, {
                        "product_id": data.product_id.id,
                        "product_qty": remaining_qty,
                        "product_uom": data.product_id.uom_po_id.id,
                        "price_unit": vendor.price or data.product_id.list_price,
                        "date_planned": fields.Datetime.now(),
                        "name": f"Vendor - {data.product_id.display_name}",
                    })],
                }
                if mo_internal_ref:
                    vendor_po_vals["mo_internal_ref"] = mo_internal_ref

                vpo = self.env["purchase.order"].create(vendor_po_vals)
                messages.append({
                    "type": "success",
                    "msg": f"✅ Vendor PO created for {data.product_id.display_name} ({remaining_qty})"
                })

                self.env['mrp.bom.context'].mark_pos_created_for_bom(bom_id)
                self.env['mrp.bom.context'].set_context_data(
                    root_bom_id, data.bom_line_id.id, data.bom_line_id.product_id.id, 'po_created', True
                )
                pos.append(vpo.id)

            else:
                messages.append({
                    "type": "info",
                    "msg": f"ℹ️ Vendor PO not created for {data.product_id.display_name}: "
                           f"Remaining quantity is {remaining_qty} (<= 0)."
                })


        action = {
            "res_model": "mrp.production",
            "name": "Manufacture Orders",
            "type": "ir.actions.act_window",
            "views": [[False, "form"]],
            "target": "current",
            "context": {"default_bom_id": bom.id,"pos":pos},
        }

        return {"action": action, "messages": messages}