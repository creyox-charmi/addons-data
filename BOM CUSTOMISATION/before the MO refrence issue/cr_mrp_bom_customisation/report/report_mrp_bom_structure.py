# # # # models/report_mrp_bom_structure.py
# # # from odoo import models
# # #
# # #
# # # class ReportBomStructure(models.AbstractModel):
# # #     _inherit = 'report.mrp.report_bom_structure'
# # #
# # #     def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False, parent_product=False, index=0, product_info=False, ignore_stock=False, simulated_leaves_per_workcenter=False):
# # #
# # #         """Override to include is_evr field in BOM data"""
# # #         data = super()._get_bom_data(
# # #             bom, warehouse, product, line_qty, bom_line, level,
# # #             parent_bom, parent_product,index, product_info, ignore_stock,simulated_leaves_per_workcenter
# # #         )
# # #
# # #         # Add is_evr field to the data
# # #         if bom:
# # #             data['is_evr'] = bom.is_evr
# # #         else:
# # #             data['is_evr'] = False
# # #
# # #         self = self.with_context(root_bom_is_evr=data['is_evr'])
# # #         print('_bom : ',data)
# # #         return data
# # #
# # #     # def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock=False):
# # #     #     """Override to include CFE quantity in component data"""
# # #     #     data = super()._get_component_data(
# # #     #         parent_bom, parent_product, warehouse,bom_line, line_quantity, level,
# # #     #         index, product_info, ignore_stock
# # #     #     )
# # #     #
# # #     #     # Add CFE quantity to component data
# # #     #     if bom_line:
# # #     #         data['cfe_quantity'] = bom_line.cfe_quantity or ''
# # #     #         data['has_cfe_quantity'] = bool(bom_line.cfe_quantity)
# # #     #     else:
# # #     #         data['cfe_quantity'] = ''
# # #     #         data['has_cfe_quantity'] = False
# # #     #
# # #     #     return data
# # #
# # #     # models/report_mrp_bom_structure.py - ADD THIS METHOD
# # #     def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index,
# # #                             product_info, ignore_stock=False):
# # #         """Override to include CFE quantity in component data"""
# # #         data = super()._get_component_data(
# # #             parent_bom, parent_product, warehouse, bom_line, line_quantity, level,
# # #             index, product_info, ignore_stock
# # #         )
# # #
# # #         # Add CFE quantity to component data
# # #         if bom_line:
# # #             data['cfe_quantity'] = bom_line.cfe_quantity or ''
# # #             data['has_cfe_quantity'] = bool(bom_line.cfe_quantity)
# # #             # Check if this component has child BOMs (not editable if it has children)
# # #             child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
# # #             data['cfe_editable'] = not bool(child_bom)
# # #             data['bom_line_id'] = bom_line.id
# # #         else:
# # #             data['cfe_quantity'] = ''
# # #             data['has_cfe_quantity'] = False
# # #             data['cfe_editable'] = False
# # #             data['bom_line_id'] = False
# # #
# # #         data['is_evr'] = bool(parent_bom and parent_bom.is_evr)
# # #
# # #         print('data : ',data)
# # #         return data
# #
# #
# #
# # # models/report_mrp_bom_structure.py
# # from odoo import models
# #
# #
# # class ReportBomStructure(models.AbstractModel):
# #     _inherit = 'report.mrp.report_bom_structure'
# #
# #     def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False, parent_product=False, index=0, product_info=False, ignore_stock=False, simulated_leaves_per_workcenter=False):
# #         """Override to include is_evr field in BOM data"""
# #         data = super()._get_bom_data(
# #             bom, warehouse, product, line_qty, bom_line, level,
# #             parent_bom,parent_product, index, product_info, ignore_stock,simulated_leaves_per_workcenter
# #         )
# #         # data['is_evr'] = bool(bom and bom.is_evr)
# #         # # 🔹 Pass the root BoM id explicitly (to propagate downwards)
# #         # data['root_bom_id'] = bom.id if bom else False
# #         # data['root_is_evr'] = bool(bom and bom.is_evr)
# #         # print('data : ',data)
# #         # return data
# #         # root BOM always comes from context
# #         root_bom_id = self.env.context.get("root_bom_id") or (bom.id if bom else False)
# #         root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
# #
# #         # 🔹 force is_evr from ROOT only
# #         data['is_evr'] = bool(root_bom and root_bom.is_evr)
# #
# #         # pass root id downwards
# #         data['root_bom_id'] = root_bom.id if root_bom else False
# #         data['root_is_evr'] = data['is_evr']
# #
# #         print(">>> BOM DATA for", data.get("name"), "is_evr=", data['is_evr'])
# #         return data
# #
# #     # def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
# #     #                         line_quantity, level, index, product_info, ignore_stock=False):
# #     #     """Inherit is_evr from the ROOT BoM (the one being viewed)"""
# #     #     data = super()._get_component_data(
# #     #         parent_bom, parent_product, warehouse, bom_line,
# #     #         line_quantity, level, index, product_info, ignore_stock
# #     #     )
# #     #
# #     #     if bom_line:
# #     #         data['cfe_quantity'] = bom_line.cfe_quantity or ''
# #     #         data['has_cfe_quantity'] = bool(bom_line.cfe_quantity)
# #     #         child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
# #     #         data['cfe_editable'] = not bool(child_bom)
# #     #         data['bom_line_id'] = bom_line.id
# #     #     else:
# #     #         data['cfe_quantity'] = ''
# #     #         data['has_cfe_quantity'] = False
# #     #         data['cfe_editable'] = False
# #     #         data['bom_line_id'] = False
# #     #
# #     #     # 🔹 Instead of parent_bom.is_evr → inherit from ROOT BoM
# #     #     root_bom_id = self.env.context.get("root_bom_id")
# #     #     root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
# #     #     if root_bom:
# #     #         data['is_evr'] = root_bom.is_evr
# #     #     else:
# #     #         # fallback to parent
# #     #         data['is_evr'] = bool(parent_bom and parent_bom.is_evr)
# #     #
# #     #     return data
# #
# #     # def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
# #     #                         line_quantity, level, index, product_info, ignore_stock=False):
# #     #     """Inherit is_evr from the ROOT BoM (the one being viewed)"""
# #     #
# #     #     print(
# #     #         f"➡️ _get_component_data called | level: {level}, index: {index}, parent_bom: {parent_bom}, product: {parent_product}")
# #     #
# #     #     data = super()._get_component_data(
# #     #         parent_bom, parent_product, warehouse, bom_line,
# #     #         line_quantity, level, index, product_info, ignore_stock
# #     #     )
# #     #     print("   Super _get_component_data returned data:", data)
# #     #
# #     #     if bom_line:
# #     #         data['cfe_quantity'] = bom_line.cfe_quantity or ''
# #     #         data['has_cfe_quantity'] = bool(bom_line.cfe_quantity)
# #     #         child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
# #     #         data['cfe_editable'] = not bool(child_bom)
# #     #         data['bom_line_id'] = bom_line.id
# #     #         print(
# #     #             f"   BOM line info | id: {bom_line.id}, cfe_quantity: {bom_line.cfe_quantity}, has child_bom: {bool(child_bom)}")
# #     #     else:
# #     #         data['cfe_quantity'] = ''
# #     #         data['has_cfe_quantity'] = False
# #     #         data['cfe_editable'] = False
# #     #         data['bom_line_id'] = False
# #     #         print("   No BOM line provided")
# #     #
# #     #     # 🔹 Instead of parent_bom.is_evr → inherit from ROOT BoM
# #     #     root_bom_id = self.env.context.get("root_bom_id")
# #     #     root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
# #     #     if root_bom:
# #     #         data['is_evr'] = root_bom.is_evr
# #     #         print(f"   ROOT BoM found | id: {root_bom.id}, is_evr: {root_bom.is_evr}")
# #     #     else:
# #     #         # fallback to parent
# #     #         data['is_evr'] = bool(parent_bom and parent_bom.is_evr)
# #     #         print(f"   No ROOT BoM, fallback | parent_bom: {parent_bom}, is_evr: {data['is_evr']}")
# #     #
# #     #     print("   Final component data:", data)
# #     #     return data
# #
# #     # models/report_mrp_bom_structure.py
# #     # def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
# #     #                         line_quantity, level, index, product_info, ignore_stock=False):
# #     #
# #     #     data = super()._get_component_data(
# #     #         parent_bom, parent_product, warehouse, bom_line,
# #     #         line_quantity, level, index, product_info, ignore_stock
# #     #     )
# #     #
# #     #     if bom_line:
# #     #         # Existing CFE logic
# #     #         data['cfe_quantity'] = bom_line.cfe_quantity or ''
# #     #         data['has_cfe_quantity'] = bool(bom_line.cfe_quantity)
# #     #         child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
# #     #         data['cfe_editable'] = not bool(child_bom)
# #     #
# #     #         # New fields
# #     #         data['lli'] = bom_line.lli
# #     #         data['approval_1'] = bom_line.approval_1
# #     #         data['approval_2'] = bom_line.approval_2
# #     #         data['lli_editable'] = not bool(child_bom)
# #     #         data['approval_1_editable'] = not bool(child_bom)
# #     #         data['approval_2_editable'] = not bool(child_bom)
# #     #     else:
# #     #         data['cfe_quantity'] = ''
# #     #         data['has_cfe_quantity'] = False
# #     #         data['cfe_editable'] = False
# #     #         data['lli'] = False
# #     #         data['approval_1'] = False
# #     #         data['approval_2'] = False
# #     #         data['lli_editable'] = False
# #     #         data['approval_1_editable'] = False
# #     #         data['approval_2_editable'] = False
# #     #
# #     #     # Inherit is_evr from ROOT BoM
# #     #     root_bom_id = self.env.context.get("root_bom_id")
# #     #     root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
# #     #     if root_bom:
# #     #         data['is_evr'] = root_bom.is_evr
# #     #     else:
# #     #         data['is_evr'] = bool(parent_bom and parent_bom.is_evr)
# #     #
# #     #     print('data : ',data)
# #     #     return
# #
# #     def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
# #                             line_quantity, level, index, product_info, ignore_stock=False):
# #
# #         data = super()._get_component_data(
# #             parent_bom, parent_product, warehouse, bom_line,
# #             line_quantity, level, index, product_info, ignore_stock
# #         )
# #
# #         if bom_line:
# #             data['bom_line_id'] = bom_line.id  # ADD THIS LINE
# #             data['cfe_quantity'] = bom_line.cfe_quantity or ''
# #             data['has_cfe_quantity'] = bool(bom_line.cfe_quantity)
# #             child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
# #             data['cfe_editable'] = not bool(child_bom)
# #
# #             data['lli'] = bom_line.lli
# #             data['approval_1'] = bom_line.approval_1
# #             data['approval_2'] = bom_line.approval_2
# #             data['lli_editable'] = not bool(child_bom)
# #             data['approval_1_editable'] = not bool(child_bom)
# #             data['approval_2_editable'] = not bool(child_bom)
# #         else:
# #             data['bom_line_id'] = False  # ADD THIS LINE
# #             data['cfe_quantity'] = ''
# #             data['has_cfe_quantity'] = False
# #             data['cfe_editable'] = False
# #             data['lli'] = False
# #             data['approval_1'] = False
# #             data['approval_2'] = False
# #             data['lli_editable'] = False
# #             data['approval_1_editable'] = False
# #             data['approval_2_editable'] = False
# #
# #         root_bom_id = self.env.context.get("root_bom_id")
# #         root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
# #         if root_bom:
# #             data['is_evr'] = root_bom.is_evr
# #         else:
# #             data['is_evr'] = bool(parent_bom and parent_bom.is_evr)
# #
# #         return dataa
# #
# #     def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
# #         # put root_bom_id in context for all recursive calls
# #         self = self.with_context(root_bom_id=bom_id)
# #         print("🔥 _get_report_data called | root_bom_id in context:", self.env.context.get("root_bom_id"))
# #         return super()._get_report_data(bom_id, searchQty, searchVariant)
# #
# #
#
#
# ## models/report_mrp_bom_structure.py
# from odoo import models
#
# class ReportBomStructure(models.AbstractModel):
#     _inherit = 'report.mrp.report_bom_structure'
#
#     def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False, parent_product=False, index=0, product_info=False, ignore_stock=False, simulated_leaves_per_workcenter=False):
#         data = super()._get_bom_data(
#             bom, warehouse, product, line_qty, bom_line, level,
#             parent_bom, parent_product, index, product_info, ignore_stock, simulated_leaves_per_workcenter
#         )
#
#         root_bom_id = self.env.context.get("root_bom_id") or (bom.id if bom else False)
#         root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
#
#         data['is_evr'] = bool(root_bom and root_bom.is_evr)
#         data['root_bom_id'] = root_bom.id if root_bom else False
#         data['root_is_evr'] = data['is_evr']
#         data['bom_id'] = bom.id if bom else False
#         print('data1 : ', data)
#         return data
#
#     def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
#                             line_quantity, level, index, product_info, ignore_stock=False):
#
#         data = super()._get_component_data(
#             parent_bom, parent_product, warehouse, bom_line,
#             line_quantity, level, index, product_info, ignore_stock
#         )
#
#         if bom_line:
#             data['cfe_quantity'] = bom_line.cfe_quantity or ''
#             data['has_cfe_quantity'] = bool(bom_line.cfe_quantity)
#             child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
#             data['cfe_editable'] = not bool(child_bom)
#             data['bom_line_id'] = bom_line.id
#
#             data['lli'] = bom_line.lli
#             data['approval_1'] = bom_line.approval_1
#             data['approval_2'] = bom_line.approval_2
#             data['lli_editable'] = not bool(child_bom)
#             data['approval_1_editable'] = not bool(child_bom)
#             data['approval_2_editable'] = not bool(child_bom)
#         else:
#             data['cfe_quantity'] = ''
#             data['has_cfe_quantity'] = False
#             data['cfe_editable'] = False
#             data['bom_line_id'] = False
#             data['lli'] = False
#             data['approval_1'] = False
#             data['approval_2'] = False
#             data['lli_editable'] = False
#             data['approval_1_editable'] = False
#             data['approval_2_editable'] = False
#
#         root_bom_id = self.env.context.get("root_bom_id")
#         root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
#         if root_bom:
#             data['is_evr'] = root_bom.is_evr
#         else:
#             data['is_evr'] = bool(parent_bom and parent_bom.is_evr)
#         print('data : ',data)
#         return data
#
#     def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
#         self = self.with_context(root_bom_id=bom_id)
#         return super()._get_report_data(bom_id, searchQty, searchVariant)
#
#
# ## models/report_mrp_bom_structure.py
# # from odoo import models, fields
# #
# # class ReportBomStructure(models.AbstractModel):
# #     _inherit = 'report.mrp.report_bom_structure'
# #
# #
# #     # def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
# #     #     print("🔹 _get_report_data CALLED")
# #     #     print(f"   ➡️ Root BOM ID: {bom_id}")
# #     #     self = self.with_context(root_bom_id=bom_id)
# #     #     return super()._get_report_data(bom_id, searchQty, searchVariant)
# #
# #     def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False,
# #                       level=0, parent_bom=False, parent_product=False, index=0,
# #                       product_info=False, ignore_stock=False, simulated_leaves_per_workcenter=False):
# #         print("🔹 _get_bom_data CALLED")
# #         print(f"   ➡️ BOM: {bom.display_name if bom else 'None'}, Product: {product.display_name if product else 'None'}, Level: {level}")
# #
# #         data = super()._get_bom_data(
# #             bom, warehouse, product, line_qty, bom_line, level,
# #             parent_bom, parent_product, index, product_info, ignore_stock, simulated_leaves_per_workcenter
# #         )
# #
# #         root_bom_id = self.env.context.get("root_bom_id") or (bom.id if bom else False)
# #         root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
# #
# #         data['is_evr'] = bool(root_bom and root_bom.is_evr)
# #         data['root_bom_id'] = root_bom.id if root_bom else False
# #         data['root_is_evr'] = data['is_evr']
# #         data['bom_id'] = bom.id if bom else False
# #
# #         print(f"   🔸 Root BOM is_evr: {data['is_evr']}")
# #         return data
# #
# #     def _collect_bom_line_values(self, bom):
# #         """Recursively collect BOM line values including the root BOM"""
# #         saved_values = {}
# #
# #         if not bom or not hasattr(bom, 'bom_line_ids'):
# #             print(f"   ⚠️ Skipping invalid BOM: {bom}")
# #             return saved_values
# #
# #         bom_display_name = bom.product_id.display_name if hasattr(bom, 'product_id') else f"BOM {bom.id}"
# #         print(f"   🔹 Collecting values for BOM: {bom_display_name} (ID {bom.id})")
# #
# #         # Include root BOM lines first
# #         for line in bom.bom_line_ids:
# #             saved_values[line.product_id.id] = {
# #                 'cfe_quantity': line.cfe_quantity or '',
# #                 'lli': line.lli,
# #                 'approval_1': line.approval_1,
# #                 'approval_2': line.approval_2
# #             }
# #
# #         # Then recursively collect from child BOMs
# #         for line in bom.bom_line_ids:
# #             child_bom = self.env['mrp.bom']._bom_find(line.product_id, bom_type='normal')
# #             if child_bom:
# #                 print(f"   🔸 Found child BOM for product {line.product_id.display_name} → {child_bom.id}")
# #                 saved_values.update(self._collect_bom_line_values(child_bom))
# #
# #         return saved_values
# #
# #     def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
# #         print("🔹 _get_report_data CALLED")
# #         print(f"   ➡️ Root BOM ID: {bom_id}")
# #         root_bom = self.env['mrp.bom'].browse(bom_id)
# #         saved_line_values = self._collect_bom_line_values(root_bom)
# #         print(f"   🔸 Collected saved_line_values (root + children): {saved_line_values}")
# #
# #         # Pass saved_line_values in context
# #         self = self.with_context(root_bom_id=bom_id, saved_line_values=saved_line_values)
# #         return super()._get_report_data(bom_id, searchQty, searchVariant)
# #
# #     def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
# #                             line_quantity, level, index, product_info, ignore_stock=False):
# #         print(f"🔹 _get_component_data CALLED")
# #         print(f"   ➡️ Parent BOM: {parent_bom}, Component: {bom_line.product_id.name if bom_line else 'N/A'}")
# #
# #         data = super()._get_component_data(
# #             parent_bom, parent_product, warehouse, bom_line,
# #             line_quantity, level, index, product_info, ignore_stock
# #         )
# #
# #         saved_values = self.env.context.get('saved_line_values') or {}
# #         if bom_line and bom_line.product_id.id in saved_values:
# #             vals = saved_values[bom_line.product_id.id]
# #             data['cfe_quantity'] = vals.get('cfe_quantity', bom_line.cfe_quantity or '')
# #             data['lli'] = vals.get('lli', bom_line.lli)
# #             data['approval_1'] = vals.get('approval_1', bom_line.approval_1)
# #             data['approval_2'] = vals.get('approval_2', bom_line.approval_2)
# #             data['has_cfe_quantity'] = bool(data['cfe_quantity'])
# #             print(f"   🔸 Overriding with saved values: {vals}")
# #         else:
# #             # fallback to actual bom_line values
# #             data['cfe_quantity'] = bom_line.cfe_quantity or ''
# #             data['lli'] = bom_line.lli
# #             data['approval_1'] = bom_line.approval_1
# #             data['approval_2'] = bom_line.approval_2
# #             data['has_cfe_quantity'] = bool(bom_line.cfe_quantity)
# #
# #         # Editable flags
# #         child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal') if bom_line else False
# #         data['cfe_editable'] = not bool(child_bom)
# #         data['lli_editable'] = not bool(child_bom)
# #         data['approval_1_editable'] = not bool(child_bom)
# #         data['approval_2_editable'] = not bool(child_bom)
# #         data['bom_line_id'] = bom_line.id if bom_line else False
# #
# #         # Root BOM is_evr
# #         root_bom_id = self.env.context.get("root_bom_id")
# #         root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
# #         data['is_evr'] = bool(root_bom and root_bom.is_evr)
# #         print(f"   🔸 Root BOM is_evr: {data['is_evr']}")
# #
# #         return data
#
#
#


## models/report_mrp_bom_structure.py
from odoo import models


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

    # def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
    #                         line_quantity, level, index, product_info, ignore_stock=False):
    #
    #     data = super()._get_component_data(
    #         parent_bom, parent_product, warehouse, bom_line,
    #         line_quantity, level, index, product_info, ignore_stock
    #     )
    #
    #     # Get root BOM ID from context
    #     root_bom_id = self.env.context.get("root_bom_id")
    #     root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
    #
    #     if bom_line and root_bom_id:
    #         # Get context-specific data based on root BOM
    #         context_data = self.env['mrp.bom.context'].get_context_data(root_bom_id, bom_line.id)
    #
    #         data['cfe_quantity'] = context_data['cfe_quantity']
    #         data['has_cfe_quantity'] = bool(context_data['cfe_quantity'])
    #         data['bom_line_id'] = bom_line.id
    #         data['lli'] = context_data['lli']
    #         data['approval_1'] = context_data['approval_1']
    #         data['approval_2'] = context_data['approval_2']
    #
    #         # Check if this component has its own BOM (child BOM)
    #         child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
    #         data['cfe_editable'] = not bool(child_bom)
    #         data['lli_editable'] = not bool(child_bom)
    #         data['approval_1_editable'] = not bool(child_bom)
    #         data['approval_2_editable'] = not bool(child_bom)
    #     else:
    #         # Default values for lines without BOM line
    #         data['cfe_quantity'] = ''
    #         data['has_cfe_quantity'] = False
    #         data['cfe_editable'] = False
    #         data['bom_line_id'] = False
    #         data['lli'] = False
    #         data['approval_1'] = False
    #         data['approval_2'] = False
    #         data['lli_editable'] = False
    #         data['approval_1_editable'] = False
    #         data['approval_2_editable'] = False
    #
    #     # Set EVR flag based on root BOM
    #     data['is_evr'] = bool(root_bom and root_bom.is_evr)
    #     data['root_bom_id'] = root_bom_id
    #
    #     return data

    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
                            line_quantity, level, index, product_info, ignore_stock=False):

        data = super()._get_component_data(
            parent_bom, parent_product, warehouse, bom_line,
            line_quantity, level, index, product_info, ignore_stock
        )

        root_bom_id = self.env.context.get("root_bom_id")
        root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False

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