# -*- coding: utf-8 -*-
from odoo import models

class ReportBomStructureBranch(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    # def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False,
    #                   parent_product=False, index=0, product_info=False, ignore_stock=False,
    #                   simulated_leaves_per_workcenter=False):
    #
    #     data = super()._get_bom_data(
    #         bom, warehouse, product, line_qty, bom_line, level,
    #         parent_bom, parent_product, index, product_info, ignore_stock, simulated_leaves_per_workcenter
    #     )
    #
    #     # Get root BOM from context or current BOM
    #     root_bom_id = self.env.context.get("root_bom_id")
    #     if not root_bom_id:
    #         root_bom_id = bom.id if bom else (parent_bom.id if parent_bom else False)
    #
    #     root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False
    #
    #     if root_bom_id and bom_line:
    #         Branch = self.env["mrp.bom.line.branch"]
    #         branch = Branch.search([
    #             ("bom_id", "=", root_bom_id),
    #             ("bom_line_id", "=", bom_line.id),
    #         ], limit=1)
    #
    #
    #         data["branch"] = branch.branch_name if branch else ""
    #
    #         if branch.branch_name:
    #             data['approve_to_manufacture_editable'] = True
    #         else:
    #             data['approve_to_manufacture_editable'] = False
    #     else:
    #         data["branch"] = ""
    #
    #     data['free_to_use'] = bom_line.free_to_use if bom_line.free_to_use else 0.0
    #     return data

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
            branch = Branch.search([
                ("bom_id", "=", root_bom_id),
                ("bom_line_id", "=", bom_line.id),
            ], limit=1)

            data["branch"] = branch.branch_name if branch else ""

            if branch.branch_name:
                data['approve_to_manufacture_editable'] = True
                data['approve_to_manufacture'] = bom_line.approve_to_manufacture
                data['display_free_to_use'] = True
                data['customer_ref_editable'] = True
            else:
                data['approve_to_manufacture_editable'] = False

            data['free_to_use'] = bom_line.free_to_use if bom_line else 0.0
            data['bom_line_id'] = bom_line.id if bom_line else False
        else:
            data["branch"] = ""
            data['free_to_use'] = 0.0
            data['bom_line_id'] = bom_line.id if bom_line else False

        return data

    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line,
                            line_quantity, level, index, product_info, ignore_stock=False):
        data = super()._get_component_data(
            parent_bom, parent_product, warehouse, bom_line,
            line_quantity, level, index, product_info, ignore_stock
        )
        data['purchase_group_editable'] = False
        if bom_line:
            root_bom_id = self.env.context.get("root_bom_id")
            root_bom = self.env['mrp.bom'].browse(root_bom_id) if root_bom_id else False

            if root_bom and root_bom.is_evr:
                data['customer_ref'] = bom_line.customer_ref or ''
                # data['po_line_id'] = bom_line.po_line_id.id if bom_line.po_line_id else False
                # data['po_line_name'] = bom_line.po_line_id.order_id.name if bom_line.po_line_id else ''

                po_line = bom_line.po_line_id
                print('po_line : ', po_line , ' po_line.order_id.state : ',po_line.order_id.state)
                if po_line and po_line.order_id.state == 'draft':
                    data['po_line_id'] = po_line.id
                    data['po_line_name'] = po_line.order_id.name
                else:
                    data['po_line_id'] = False
                    data['po_line_name'] = ''

                child_bom = self.env['mrp.bom']._bom_find(bom_line.product_id, bom_type='normal')
                data['customer_ref_editable'] = not bool(child_bom)

                # Purchase group fields
                data['purchase_group_editable'] = bom_line.approval_1 and bom_line.approval_2
                data['to_order'] = bom_line.to_order if bom_line.to_order is not False else None
                data['to_order_cfe'] = bom_line.to_order_cfe if bom_line.to_order_cfe is not False else None
                data['ordered'] = bom_line.ordered if bom_line.ordered is not False else None
                data['ordered_cfe'] = bom_line.ordered_cfe if bom_line.ordered_cfe is not False else None
                data['to_transfer'] = bom_line.to_transfer if bom_line.to_transfer is not False else None
                data['to_transfer_cfe'] = bom_line.to_transfer_cfe if bom_line.to_transfer_cfe is not False else None
                data['transferred'] = bom_line.transferred if bom_line.transferred is not False else None
                data['transferred_cfe'] = bom_line.transferred_cfe if bom_line.transferred_cfe is not False else None
                data['used'] = bom_line.used if bom_line.used is not False else None
                data['free_to_use'] = bom_line.free_to_use
                data['display_free_to_use'] = not bool(child_bom)


        return data
