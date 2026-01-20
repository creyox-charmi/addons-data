# # -*- coding: utf-8 -*-
# from odoo import models,api
#
# class ReportBomStructureBranch(models.AbstractModel):
#     _inherit = 'report.mrp.report_bom_structure'
#
#     def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False,
#                       parent_product=False, index=0, product_info=False, ignore_stock=False,
#                       simulated_leaves_per_workcenter=False):
#         data = super()._get_bom_data(
#             bom, warehouse, product, line_qty, bom_line, level,
#             parent_bom, parent_product, index, product_info, ignore_stock, simulated_leaves_per_workcenter
#         )
#
#         # Get root BOM from context or current BOM
#         root_bom_id = self.env.context.get("root_bom_id")
#         if not root_bom_id:
#             root_bom_id = bom.id if bom else (parent_bom.id if parent_bom else False)
#         root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
#
#         if root_bom_id and bom_line:
#             Branch = self.env["mrp.bom.line.branch"]
#
#             # Get all branches for this bom_id and bom_line_id combination, ordered by sequence
#             branches = Branch.search([
#                 ("bom_id", "=", root_bom_id),
#                 ("bom_line_id", "=", bom_line.id),
#             ], order='sequence')
#
#             branch = False
#             if branches:
#                 if len(branches) == 1:
#                     # Only one branch for this bom_line, use it
#                     branch = branches[0]
#                 else:
#                     # Multiple branches exist for this bom_line_id
#                     index_str = str(index)
#                     path_key = f"{root_bom_id}_{bom_line.id}_{index_str}"
#
#                     # Use a class variable or cache to persist across all calls
#                     # This ensures the counter persists across the entire BOM traversal
#                     if not hasattr(self.__class__, '_branch_assignment_cache'):
#                         self.__class__._branch_assignment_cache = {}
#
#                     cache = self.__class__._branch_assignment_cache
#
#                     # Create a cache key for this specific BOM report generation
#                     # Use root_bom_id as the cache namespace
#                     cache_key = f"bom_{root_bom_id}"
#                     if cache_key not in cache:
#                         cache[cache_key] = {
#                             'assignments': {},
#                             'seen_paths': []
#                         }
#
#                     bom_cache = cache[cache_key]
#
#                     if path_key not in bom_cache['seen_paths']:
#                         # First time seeing this path
#                         # Count how many different paths for this bom_line we've seen
#                         existing_count = len([p for p in bom_cache['seen_paths']
#                                               if p.startswith(f"{root_bom_id}_{bom_line.id}_")])
#
#                         # Assign branch based on count
#                         if existing_count < len(branches):
#                             branch = branches[existing_count]
#                         else:
#                             branch = branches[-1]
#
#                         # Store assignment
#                         bom_cache['assignments'][path_key] = branch.id
#                         bom_cache['seen_paths'].append(path_key)
#                     else:
#                         # Path already seen (duplicate call), reuse assignment
#                         branch_id = bom_cache['assignments'].get(path_key)
#                         branch = Branch.browse(branch_id) if branch_id else False
#
#                     # Clean up cache if we're at level 0 (end of traversal)
#                     if level == 0 and not bom_line:
#                         # Clear this BOM's cache after processing is complete
#                         if cache_key in cache:
#                             del cache[cache_key]
#
#             data["branch"] = branch.branch_name if branch else ""
#             if branch and branch.branch_name:
#                 data['approve_to_manufacture_editable'] = True
#                 data['approve_to_manufacture'] = bom_line.approve_to_manufacture
#                 data['display_free_to_use'] = True
#                 data['customer_ref_editable'] = True
#             else:
#                 data['approve_to_manufacture_editable'] = False
#
#             # data['free_to_use'] = bom_line.free_to_use if bom_line else 0.0
#             data['bom_line_id'] = bom_line.id if bom_line else False
#         else:
#             data["branch"] = ""
#             data['free_to_use'] = 0.0
#             data['bom_line_id'] = bom_line.id if bom_line else False
#
#
#         return data
#
#
#     def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
#                             line_quantity, level, index, product_info, ignore_stock=False):
#         data = super()._get_component_data(
#             parent_bom, parent_product, warehouse, bom_line,
#             line_quantity, level, index, product_info, ignore_stock
#         )
#         data['purchase_group_editable'] = False
#         if bom_line:
#             root_bom_id = self.env.context.get("root_bom_id")
#             root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
#
#             if root_bom and root_bom.is_evr:
#                 data['customer_ref'] = bom_line.customer_ref or ''
#                 # data['po_line_id'] = bom_line.po_line_id.id if bom_line.po_line_id else False
#                 # data['po_line_name'] = bom_line.po_line_id.order_id.name if bom_line.po_line_id else ''
#
#                 po_line = bom_line.po_line_id
#                 if po_line and po_line.order_id.state == 'draft':
#                     data['po_line_id'] = po_line.id
#                     data['po_line_name'] = po_line.order_id.name
#                 else:
#                     data['po_line_id'] = False
#                     data['po_line_name'] = ''
#
#                 child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
#                 data['customer_ref_editable'] = not bool(child_bom)
#
#                 # Purchase group fields
#                 data['purchase_group_editable'] = bom_line.approval_1 and bom_line.approval_2
#                 is_approval = bom_line.approval_1 and bom_line.approval_2
#                 if is_approval:
#                     data['to_order'] = bom_line.to_order if bom_line.to_order is not False else None
#                     data['to_order_cfe'] = bom_line.to_order_cfe if bom_line.to_order_cfe is not False else None
#                     data['ordered'] = bom_line.ordered if bom_line.ordered is not False else None
#                     data['ordered_cfe'] = bom_line.ordered_cfe if bom_line.ordered_cfe is not False else None
#                     data['to_transfer'] = bom_line.to_transfer if bom_line.to_transfer is not False else None
#                     data['to_transfer_cfe'] = bom_line.to_transfer_cfe if bom_line.to_transfer_cfe is not False else None
#                     data['transferred'] = bom_line.transferred if bom_line.transferred is not False else None
#                     data['transferred_cfe'] = bom_line.transferred_cfe if bom_line.transferred_cfe is not False else None
#                     data['used'] = bom_line.used if bom_line.used is not False else None
#                 else:
#                     data['to_order'] = None
#                     data['to_order_cfe'] = None
#                     data['ordered'] = None
#                     data['ordered_cfe'] = None
#                     data['to_transfer'] = None
#                     data['to_transfer_cfe'] = None
#                     data['transferred'] = None
#                     data['transferred_cfe'] = None
#                     data['used'] = None
#
#                 data['free_to_use'] = bom_line.free_to_use
#                 data['display_free_to_use'] = not bool(child_bom)
#
#
#         return data
#
#
#     def _get_branch_for_component(self, root_bom_id, bom_line, index):
#         """
#         Get the parent BOM's branch record for this component line.
#         This finds the branch of the BOM that contains this line.
#         """
#         Branch = self.env["mrp.bom.line.branch"]
#
#         # Find parent BOM line that contains this bom_line
#         parent_bom_line = self.env['mrp.bom.line'].search([
#             ('child_bom_id', '=', bom_line.bom_id.id)
#         ], limit=1)
#
#         if not parent_bom_line:
#             return False
#
#         # Get branches for parent BOM line
#         branches = Branch.search([
#             ("bom_id", "=", root_bom_id),
#             ("bom_line_id", "=", parent_bom_line.id),
#         ], order='sequence')
#
#         if not branches:
#             return False
#
#         if len(branches) == 1:
#             return branches[0]
#
#         # Multiple branches - use cache logic (same as _get_bom_data)
#         index_str = str(index)
#         path_key = f"{root_bom_id}_{parent_bom_line.id}_{index_str}"
#
#         if not hasattr(self.__class__, '_branch_assignment_cache'):
#             return branches[0]
#
#         cache = self.__class__._branch_assignment_cache
#         cache_key = f"bom_{root_bom_id}"
#
#         if cache_key not in cache:
#             return branches[0]
#
#         bom_cache = cache[cache_key]
#
#         if path_key in bom_cache['assignments']:
#             branch_id = bom_cache['assignments'].get(path_key)
#             return Branch.browse(branch_id) if branch_id else branches[0]
#
#         return branches[0]


# -*- coding: utf-8 -*-
from odoo import models, api


class ReportBomStructureBranch(models.AbstractModel):
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

        if root_bom_id and bom_line:
            Branch = self.env["mrp.bom.line.branch"]

            # Get all branches for this bom_id and bom_line_id combination, ordered by sequence
            branches = Branch.search([
                ("bom_id", "=", root_bom_id),
                ("bom_line_id", "=", bom_line.id),
            ], order='sequence')

            branch = False
            if branches:
                if len(branches) == 1:
                    # Only one branch for this bom_line, use it
                    branch = branches[0]
                else:
                    # Multiple branches exist for this bom_line_id
                    index_str = str(index)
                    path_key = f"{root_bom_id}_{bom_line.id}_{index_str}"

                    # Use a class variable or cache to persist across all calls
                    if not hasattr(self.__class__, '_branch_assignment_cache'):
                        self.__class__._branch_assignment_cache = {}

                    cache = self.__class__._branch_assignment_cache
                    cache_key = f"bom_{root_bom_id}"
                    if cache_key not in cache:
                        cache[cache_key] = {
                            'assignments': {},
                            'seen_paths': []
                        }

                    bom_cache = cache[cache_key]

                    if path_key not in bom_cache['seen_paths']:
                        existing_count = len([p for p in bom_cache['seen_paths']
                                              if p.startswith(f"{root_bom_id}_{bom_line.id}_")])

                        if existing_count < len(branches):
                            branch = branches[existing_count]
                        else:
                            branch = branches[-1]

                        bom_cache['assignments'][path_key] = branch.id
                        bom_cache['seen_paths'].append(path_key)
                    else:
                        branch_id = bom_cache['assignments'].get(path_key)
                        branch = Branch.browse(branch_id) if branch_id else False

                    if level == 0 and not bom_line:
                        if cache_key in cache:
                            del cache[cache_key]

            data["branch"] = branch.branch_name if branch else ""
            data["free_to_use"] = branch.free_to_use
            if branch and branch.branch_name:
                data['approve_to_manufacture_editable'] = True
                data['approve_to_manufacture'] = bom_line.approve_to_manufacture
                data['display_free_to_use'] = True
                data['customer_ref_editable'] = True
            else:
                data['approve_to_manufacture_editable'] = False

            data['bom_line_id'] = bom_line.id if bom_line else False

        else:
            data["branch"] = ""
            data['free_to_use'] = 0.0
            data['bom_line_id'] = bom_line.id if bom_line else False

        # data['approve_to_manufacture_editable'] = True
        print('data : ',data)
        return data

    # def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
    #                         line_quantity, level, index, product_info, ignore_stock=False):
    #     data = super()._get_component_data(
    #         parent_bom, parent_product, warehouse, bom_line,
    #         line_quantity, level, index, product_info, ignore_stock
    #     )
    #     data['purchase_group_editable'] = False
    #
    #     if bom_line:
    #         print('bom_line : ',bom_line)
    #         root_bom_id = self.env.context.get("root_bom_id")
    #         root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
    #
    #         if root_bom and root_bom.is_evr:
    #             data['customer_ref'] = bom_line.customer_ref or ''
    #
    #             po_line = bom_line.po_line_id
    #             if po_line and po_line.order_id.state == 'draft':
    #                 data['po_line_id'] = po_line.id
    #                 data['po_line_name'] = po_line.order_id.name
    #             else:
    #                 data['po_line_id'] = False
    #                 data['po_line_name'] = ''
    #
    #             child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
    #             print('child_bom : ',child_bom)
    #             data['customer_ref_editable'] = not bool(child_bom)
    #
    #             # 🔥 Get component record for this line
    #             component_rec = self._get_component_for_line(root_bom_id, bom_line, parent_bom, index)
    #             print('component_rec : ', component_rec)
    #             # Purchase group fields from component record
    #             data['purchase_group_editable'] = bom_line.approval_1 and bom_line.approval_2
    #             is_approval = bom_line.approval_1 and bom_line.approval_2
    #
    #             if is_approval and component_rec:
    #                 data['to_order'] = component_rec.to_order
    #                 data['to_order_cfe'] = component_rec.to_order_cfe
    #                 data['ordered'] = component_rec.ordered
    #                 data['ordered_cfe'] = component_rec.ordered_cfe
    #                 data['to_transfer'] = component_rec.to_transfer
    #                 data['to_transfer_cfe'] = component_rec.to_transfer_cfe
    #                 data['transferred'] = component_rec.transferred
    #                 data['transferred_cfe'] = component_rec.transferred_cfe
    #                 data['used'] = component_rec.used
    #                 data['free_to_use'] = component_rec.free_to_use
    #             else:
    #                 data['to_order'] = None
    #                 data['to_order_cfe'] = None
    #                 data['ordered'] = None
    #                 data['ordered_cfe'] = None
    #                 data['to_transfer'] = None
    #                 data['to_transfer_cfe'] = None
    #                 data['transferred'] = None
    #                 data['transferred_cfe'] = None
    #                 data['used'] = None
    #                 data['free_to_use'] = None
    #
    #
    #             data['display_free_to_use'] = None
    #
    #     return data

    # def _get_component_for_line(self, root_bom_id, bom_line, parent_bom, index):
    #     """
    #     Get the component record using the same cache logic as branch assignment
    #     """
    #     Component = self.env["mrp.bom.line.branch.components"]
    #
    #     # Check if this line has a child BOM
    #     child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
    #     print('===============================')
    #     print('child_bom : ',child_bom)
    #     if child_bom:
    #         return False
    #
    #     # Find parent BOM line that contains this line
    #     parent_bom_line = self.env['mrp.bom.line'].search([
    #         ('child_bom_id', '=', bom_line.bom_id.id)
    #     ], limit=1)
    #     print('parent_bom_line  : ',parent_bom_line)
    #
    #     if not parent_bom_line:
    #         # Root-level direct component
    #         component = Component.search([
    #             ('root_bom_id', '=', root_bom_id),
    #             ('cr_bom_line_id', '=', bom_line.id),
    #             ('is_direct_component', '=', True),
    #         ], limit=1)
    #         return component if component else False
    #
    #     # 🔥 Use cache to get the right component (same logic as branch)
    #     index_str = str(index)
    #     path_key = f"{root_bom_id}_{parent_bom_line.id}_{index_str}"
    #
    #     if not hasattr(self.__class__, '_branch_assignment_cache'):
    #         return False
    #
    #     cache = self.__class__._branch_assignment_cache
    #     cache_key = f"bom_{root_bom_id}"
    #
    #     if cache_key not in cache:
    #         return False
    #
    #     bom_cache = cache[cache_key]
    #
    #     # 🔥 Get branch_id from cache (same path_key used in _get_bom_data)
    #     if path_key not in bom_cache['assignments']:
    #         return False
    #
    #     branch_id = bom_cache['assignments'].get(path_key)
    #     if not branch_id:
    #         return False
    #
    #     # 🔥 Now find component using this branch_id and bom_line.id
    #     component = Component.search([
    #         ('bom_line_branch_id', '=', branch_id),
    #         ('cr_bom_line_id', '=', bom_line.id),
    #     ], limit=1)
    #
    #     return component if component else False

    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
                            line_quantity, level, index, product_info, ignore_stock=False):

        data = super()._get_component_data(
            parent_bom, parent_product, warehouse, bom_line,
            line_quantity, level, index, product_info, ignore_stock
        )

        data['purchase_group_editable'] = False

        if not bom_line:
            return data

        root_bom_id = self.env.context.get("root_bom_id")

        root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False

        if not root_bom:
            return data


        if not root_bom.is_evr:
            return data

        data['customer_ref'] = bom_line.customer_ref or ''

        # po_line = bom_line.po_line_id
        # if po_line and po_line.order_id.state == 'draft':
        #     data['po_line_id'] = po_line.id
        #     data['po_line_name'] = po_line.order_id.name
        # else:
        #     data['po_line_id'] = False
        #     data['po_line_name'] = ''

        # -------------------------------
        # PURCHASE ORDER HANDLING (MERGED SINGLE FIELD)
        # -------------------------------
        po_ids = []
        po_names = []

        # Vendor PO
        po_line = bom_line.po_line_id
        if po_line and po_line.order_id.state == 'draft':
            po_ids.append(po_line.id)
            po_names.append(po_line.order_id.name)

        # Customer PO
        cust_po_line = bom_line.customer_po_line_id
        if cust_po_line and cust_po_line.order_id.state == 'draft':
            po_ids.append(cust_po_line.id)
            po_names.append(cust_po_line.order_id.name)

        # Store into SAME keys
        data['po_line_id'] = po_ids or False
        data['po_line_name'] = ", ".join(po_names) if po_names else ""

        child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')

        data['customer_ref_editable'] = not bool(child_bom)

        component_rec = self._get_component_for_line(root_bom_id, bom_line, parent_bom, index)
        data['display_free_to_use'] = True
        if component_rec:
            data['free_to_use'] = component_rec.free_to_use
        # print("data['free_to_use']:", data['free_to_use'])

        data['purchase_group_editable'] = bom_line.approval_1 and bom_line.approval_2
        is_approval = bom_line.approval_1 and bom_line.approval_2

        if is_approval and component_rec:
            print("✅ DATA POPULATED FROM COMPONENT")
            data['to_order'] = component_rec.to_order
            data['to_order_cfe'] = component_rec.to_order_cfe
            data['ordered'] = component_rec.ordered
            data['ordered_cfe'] = component_rec.ordered_cfe
            data['to_transfer'] = component_rec.to_transfer
            data['to_transfer_cfe'] = component_rec.to_transfer_cfe
            data['transferred'] = component_rec.transferred
            data['transferred_cfe'] = component_rec.transferred_cfe
            data['used'] = component_rec.used

        else:
            print("❌ COMPONENT NOT USED (approval or record missing)")
            data['to_order'] = None
            data['to_order_cfe'] = None
            data['ordered'] = None
            data['ordered_cfe'] = None
            data['to_transfer'] = None
            data['to_transfer_cfe'] = None
            data['transferred'] = None
            data['transferred_cfe'] = None
            data['used'] = None


        print("================ END COMPONENT DATA ================\n")
        return data


    # def _get_component_for_line(self, root_bom_id, bom_line, parent_bom, index):
    #     print("\n--- _get_component_for_line() ---")
    #     print(
    #         f" root_bom_id={root_bom_id}, bom_line={bom_line.id}, parent_bom={parent_bom.id if parent_bom else None}, index={index}")
    #
    #     Component = self.env["mrp.bom.line.branch.components"]
    #
    #     # Check for child BOM
    #     child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
    #     print(f" child_bom: {child_bom}")
    #
    #     if child_bom:
    #         print(" → Exiting: child BOM exists")
    #         return False
    #
    #     # ROOT LEVEL COMPONENT
    #     if not parent_bom or parent_bom.id == root_bom_id:
    #         print(" Case: ROOT LEVEL COMPONENT")
    #
    #         components = Component.search([
    #             ('root_bom_id', '=', root_bom_id),
    #             ('bom_id', '=', parent_bom.id),
    #             ('cr_bom_line_id', '=', bom_line.id),
    #             ('is_direct_component', '=', True),
    #         ])
    #         print(f"  components found: {[c.id for c in components]}")
    #
    #         if not components:
    #             print("   → None found")
    #             return False
    #
    #         if len(components) == 1:
    #             print(f"   → Returning single component: {components[0].id}")
    #             return components[0]
    #
    #         try:
    #             comp = components[int(index)]
    #             print(f"   → Returning indexed component: {comp.id}")
    #             return comp
    #         except (IndexError, ValueError):
    #             print(f"   → Invalid index, returning default: {components[0].id}")
    #             return components[0]
    #
    #     # CHILD LEVEL COMPONENT
    #     print(" Case: CHILD LEVEL COMPONENT")
    #     print(" Matching parent_bom_line from parent_bom.bom_line_ids...")
    #
    #
    #     components = Component.search([
    #         ('root_bom_id', '=', root_bom_id),
    #         ('bom_id', '=', parent_bom.id),
    #         ('cr_bom_line_id','=',bom_line.id),
    #         ('is_direct_component', '=', False),
    #     ])
    #
    #     print(f" components found: {[c.id for c in components]}")
    #
    #     if len(components) == 1:
    #         return components[0]
    #
    #         # Multiple branches - use cache logic
    #     index_str = str(index)
    #     path_key = f"{root_bom_id}_{bom_line.id}_{index_str}"
    #
    #     if not hasattr(self.__class__, '_branch_component_assignment_cache'):
    #         return components[0]
    #
    #     cache = self.__class__._branch_component_assignment_cache
    #     cache_key = f"bom_{root_bom_id}"
    #
    #     if cache_key not in cache:
    #         return components[0]
    #
    #     bom_cache = cache[cache_key]
    #
    #     if path_key in bom_cache['assignments']:
    #         component_id = bom_cache['assignments'].get(path_key)
    #         return components.browse(component_id) if component_id else components[0]
    #
    #     return components[0]

    def _get_component_for_line(self, root_bom_id, bom_line, parent_bom, index):
        print("\n--- _get_component_for_line() ---")
        print(
            f" root_bom_id={root_bom_id}, bom_line={bom_line.id}, parent_bom={parent_bom.id if parent_bom else None}, index={index}")

        Component = self.env["mrp.bom.line.branch.components"]

        # Check for child BOM
        child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
        print(f" child_bom: {child_bom}")

        if child_bom:
            print(" → Exiting: child BOM exists")
            return False

        # ROOT LEVEL COMPONENT
        if not parent_bom or parent_bom.id == root_bom_id:
            print(" Case: ROOT LEVEL COMPONENT")

            components = Component.search([
                ('root_bom_id', '=', root_bom_id),
                ('bom_id', '=', parent_bom.id),
                ('cr_bom_line_id', '=', bom_line.id),
                ('is_direct_component', '=', True),
            ])
            print(f"  components found: {[c.id for c in components]}")

            if not components:
                print("   → None found")
                return False

            if len(components) == 1:
                print(f"   → Returning single component: {components[0].id}")
                return components[0]

            try:
                comp = components[int(index)]
                print(f"   → Returning indexed component: {comp.id}")
                return comp
            except (IndexError, ValueError):
                print(f"   → Invalid index, returning default: {components[0].id}")
                return components[0]

        # CHILD LEVEL COMPONENT
        print(" Case: CHILD LEVEL COMPONENT")

        components = Component.search([
            ('root_bom_id', '=', root_bom_id),
            ('bom_id', '=', parent_bom.id),
            ('cr_bom_line_id', '=', bom_line.id),
            ('is_direct_component', '=', False),
        ], order='id')

        print(f" components found: {[c.id for c in components]}")

        if not components:
            return False

        if len(components) == 1:
            return components[0]

        # Multiple components - use cache logic
        index_str = str(index)
        path_key = f"{root_bom_id}_{bom_line.id}_{index_str}"

        if not hasattr(self.__class__, '_branch_assignment_cache'):
            self.__class__._branch_assignment_cache = {}

        cache = self.__class__._branch_assignment_cache
        cache_key = f"bom_{root_bom_id}"

        if cache_key not in cache:
            cache[cache_key] = {
                'assignments': {},
                'seen_paths': []
            }

        bom_cache = cache[cache_key]

        if path_key not in bom_cache['seen_paths']:
            # First time seeing this path
            existing_count = len([p for p in bom_cache['seen_paths']
                                  if p.startswith(f"{root_bom_id}_{bom_line.id}_")])

            if existing_count < len(components):
                component = components[existing_count]
            else:
                component = components[-1]

            bom_cache['assignments'][path_key] = component.id
            bom_cache['seen_paths'].append(path_key)
            return component
        else:
            # Path already seen, reuse assignment
            component_id = bom_cache['assignments'].get(path_key)
            return Component.browse(component_id) if component_id else components[0]

    def _get_branch_for_parent(self, root_bom_id, parent_bom_line, index):
        """
        Get the branch record for a parent BOM line.
        Uses the same cache logic as _get_bom_data to ensure consistency.
        """
        Branch = self.env["mrp.bom.line.branch"]

        # Get branches for parent BOM line
        branches = Branch.search([
            ("bom_id", "=", root_bom_id),
            ("bom_line_id", "=", parent_bom_line.id),
        ], order='sequence')

        if not branches:
            return False

        if len(branches) == 1:
            return branches[0]

        # Multiple branches - use cache logic
        index_str = str(index)
        path_key = f"{root_bom_id}_{parent_bom_line.id}_{index_str}"

        if not hasattr(self.__class__, '_branch_assignment_cache'):
            return branches[0]

        cache = self.__class__._branch_assignment_cache
        cache_key = f"bom_{root_bom_id}"

        if cache_key not in cache:
            return branches[0]

        bom_cache = cache[cache_key]

        if path_key in bom_cache['assignments']:
            branch_id = bom_cache['assignments'].get(path_key)
            return Branch.browse(branch_id) if branch_id else branches[0]

        return branches[0]

