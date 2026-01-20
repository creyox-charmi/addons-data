## models/report_mrp_bom_structure.py
from odoo import models
import base64

class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False,
                      parent_product=False, index=0, product_info=False, ignore_stock=False,
                      simulated_leaves_per_workcenter=False):
        data = super()._get_bom_data(
            bom, warehouse, product, line_qty, bom_line, level,
            parent_bom, parent_product, index, product_info, ignore_stock, simulated_leaves_per_workcenter
        )

        # Get root BOM from context or current BOM
        root_bom_id = self.env.context.get("root_bom_id")
        if not root_bom_id:
            root_bom_id = bom.id if bom else (parent_bom.id if parent_bom else False)

        root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False

        data['is_evr'] = bool(root_bom and root_bom.is_evr)
        data['bom_id'] = bom.id if bom else False
        data['root_bom_id'] = root_bom_id
        data['root_is_evr'] = data['is_evr']

        return data



    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
                            line_quantity, level, index, product_info, ignore_stock=False):

        data = super()._get_component_data(
            parent_bom, parent_product, warehouse, bom_line,
            line_quantity, level, index, product_info, ignore_stock
        )

        root_bom_id = self.env.context.get("root_bom_id")
        root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False

        # Debug image handling in _get_component_data method
        if bom_line and bom_line.product_id:
            data['product_id'] = bom_line.product_id.id
            data['product_name'] = bom_line.product_id.display_name

            # Debug image field
            image_field = bom_line.product_id.image_128
            print(f"Image field type: {type(image_field)}")
            print(f"Image field value: {bool(image_field)}")

            if image_field:
                try:
                    # Method 1: Direct assignment (if it's already base64 string)
                    if isinstance(image_field, str):
                        data['product_image'] = image_field
                        print("Using direct string assignment")
                    # Method 2: Binary to base64 conversion
                    elif isinstance(image_field, bytes):
                        data['product_image'] = base64.b64encode(image_field).decode('utf-8')
                        print("Converting bytes to base64")
                    else:
                        # Method 3: For other field types
                        data['product_image'] = str(image_field)
                        print(f"Using string conversion for type: {type(image_field)}")
                except Exception as e:
                    print(f"Image conversion error: {e}")
                    data['product_image'] = False
            else:
                data['product_image'] = False

        if bom_line and root_bom_id:
            # Context-specific data
            context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, bom_line.id)

            data['cfe_quantity'] = context_data['cfe_quantity']
            data['has_cfe_quantity'] = bool(context_data['cfe_quantity'])
            data['bom_line_id'] = bom_line.id
            data['lli'] = context_data['lli']
            data['approval_1'] = context_data['approval_1']
            data['approval_2'] = context_data['approval_2']

            child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
            data['cfe_editable'] = not bool(child_bom)
            data['lli_editable'] = not bool(child_bom)
            data['approval_1_editable'] = not bool(child_bom)
            data['approval_2_editable'] = not bool(child_bom)
            data['mo_internal_ref_editable'] = not bool(child_bom)
            data['has_mo_internal_ref'] = bool(context_data['mo_internal_ref'])



            # -------------------------------
            # ✅ New: Available Vendors + Selected Vendor
            # -------------------------------
            available_vendors = [
                {
                    'id': seller.id,
                    'partner_id': seller.partner_id.id,
                    'display_name': seller.partner_id.display_name,
                }
                for seller in bom_line.product_id.seller_ids
            ]

            data['available_vendors'] = available_vendors
            print('>> ',context_data['mo_internal_ref'])
            partner = self.env['res.partner'].browse(context_data['mo_internal_ref'])
            print('>>>>>> ',partner)
            data['mo_internal_ref'] = partner.id if partner else False
            data['mo_internal_ref_name'] = partner.display_name if partner else ''

            # data['mo_internal_ref'] = context_data['mo_internal_ref'] if context_data['mo_internal_ref'] else False
        else:
            # Defaults
            data.update({
                'cfe_quantity': '',
                'has_cfe_quantity': False,
                'cfe_editable': False,
                'bom_line_id': False,
                'lli': False,
                'approval_1': False,
                'approval_2': False,
                'lli_editable': False,
                'approval_1_editable': False,
                'approval_2_editable': False,
                'available_vendors': [],
                'mo_internal_ref': False,
            })

        data['is_evr'] = bool(root_bom and root_bom.is_evr)
        data['root_bom_id'] = root_bom_id
        print('data : ',data)
        return data

    def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
        # Set root BOM context for the entire report
        self = self.with_context(root_bom_id=bom_id)
        return super()._get_report_data(bom_id, searchQty, searchVariant)