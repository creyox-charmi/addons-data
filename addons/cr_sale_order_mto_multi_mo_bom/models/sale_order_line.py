# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, api
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        re_lines = self.filtered(lambda l: (
                l.re_nre == 're' and
                l.product_id.qty_available <= 0 and
                l.product_id.route_ids.filtered(lambda r: 'Replenish on Order (MTO)' in r.name) and
                l.product_id.route_ids.filtered(lambda r: 'Manufacture' in r.name)
        ))

        normal_lines = self - re_lines

        if re_lines:
            re_lines._handle_re_procurement(previous_product_uom_qty)

        if normal_lines:
            return super(SaleOrderLine, normal_lines)._action_launch_stock_rule()

        return True

    def _handle_re_procurement(self, previous_product_uom_qty=False):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self:
            line_qty = line.product_uom_qty - (
                previous_product_uom_qty.get(line, 0.0) if previous_product_uom_qty else 0.0)
            if float_compare(line_qty, 0.0, precision_digits=precision) <= 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id

            qty = int(line.product_uom_qty)
            order_name = line.order_id.name
            sale_order_prefix = order_name[-5:] if len(order_name) >= 5 else order_name
            everest_pn = line.everest_pn or ''

            main_bom_ref = f"EVR{sale_order_prefix}"
            layer2_bom_ref = everest_pn

            layer1_product = line._create_phantom_product(main_bom_ref, line.product_id)
            layer2_product = line._create_phantom_product(layer2_bom_ref, line.product_id)

            main_bom = line._create_or_get_bom(layer1_product, main_bom_ref, None)
            layer2_bom = line._create_or_get_bom(layer2_product, layer2_bom_ref, main_bom)

            warehouse = line.order_id.warehouse_id
            location = warehouse.lot_stock_id

            for i in range(1, qty + 1):
                part_number = f"{everest_pn}.{str(i).zfill(2)}"

                mo_vals = {
                    'product_id': line.product_id.id,
                    'product_qty': 1.0,
                    'product_uom_id': line.product_uom.id,
                    'location_src_id': location.id,
                    'location_dest_id': location.id,
                    'origin': line.order_id.name,
                    'company_id': line.company_id.id,
                    'part_number': part_number,
                    'procurement_group_id': group_id.id,
                }

                self.env['mrp.production'].create(mo_vals)

    def _create_phantom_product(self, product_ref, base_product):
        product = self.env['product.product'].search([
            ('default_code', '=', product_ref)
        ], limit=1)

        if not product:
            product_vals = {
                'name': f"{base_product.name} - {product_ref}",
                'default_code': product_ref,
                'type': 'product',
                'categ_id': base_product.categ_id.id,
                'uom_id': base_product.uom_id.id,
                'uom_po_id': base_product.uom_po_id.id,
                'type': 'consu',
            }
            product = self.env['product.product'].create(product_vals)

        return product

    def _create_or_get_bom(self, product, bom_ref, parent_bom):
        bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('code', '=', bom_ref)
        ], limit=1)

        if not bom:
            bom_vals = {
                'product_tmpl_id': product.product_tmpl_id.id,
                'product_id': product.id,
                'product_qty': 1.0,
                'code': bom_ref,
                'type': 'phantom',
            }
            bom = self.env['mrp.bom'].create(bom_vals)

        if parent_bom:
            existing_line = self.env['mrp.bom.line'].search([
                ('bom_id', '=', parent_bom.id),
                ('product_id', '=', product.id)
            ], limit=1)

            if not existing_line:
                self.env['mrp.bom.line'].create({
                    'bom_id': parent_bom.id,
                    'product_id': product.id,
                    'product_qty': 1.0,
                })

        return bom