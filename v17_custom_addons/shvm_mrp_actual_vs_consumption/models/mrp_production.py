# -*- coding: utf-8 -*-
# Email: sales@creyox.com

from odoo import models, fields, api, _


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    consumption_ids = fields.One2many('mrp.consumption.ratio', 'production_id',
                                      help='It shows the actual consumption ratio of material according to the BoM.')

    def calculate_consumption_component(self):
        self.consumption_ids = False
        for record in self:
            bom_data = []
            if record.state not in ['draft', 'cancel'] and record.bom_id and record.bom_id.bom_line_ids \
                and record.qty_producing > 0:
                record.consumption_ids = False
                for bom_line in record.bom_id.bom_line_ids:
                    consumed_qty = 0
                    ratio = 0
                    ratio_type = ''
                    to_consume = 0
                    consumed_product = self.env['stock.move'].search(
                        [('raw_material_production_id', '=', record.id or record._origin.id),
                         ('product_id', '=', bom_line.product_id.id)], limit=1)
                    if consumed_product:
                        consumed_qty = consumed_product.quantity
                        to_consume = (record.qty_producing * bom_line.product_qty) / record.bom_id.product_qty
                        if consumed_qty > 0:
                            ratio = (consumed_qty * 100) / to_consume
                            if ratio > 100:
                                ratio = 100 - ratio
                                ratio_type = 'higher'
                            elif 0 < ratio < 100:
                                ratio = 100 - ratio
                                ratio_type = 'lower'
                            else:
                                ratio_type = 'accurate'
                    line = {
                        'product_id': bom_line.product_id.id,
                        'production_id': record.id,
                        'to_consume': to_consume,
                        'uom_id': bom_line.product_uom_id.id,
                        'actual_consume': consumed_qty,
                        'ratio': '%.2f%%' % ratio,
                        'ratio_type': ratio_type,
                    }
                    bom_data.append((0, 0, line))
            record.consumption_ids = bom_data

    def button_mark_done(self):
        res = super(MRPProduction, self).button_mark_done()
        self.calculate_consumption_component()
        return res


class MrpConsumptionRatio(models.Model):
    _name = 'mrp.consumption.ratio'
    _description = 'MRP Consumption Ratio'

    production_id = fields.Many2one('mrp.production')
    product_id = fields.Many2one('product.product')
    to_consume = fields.Float()
    actual_consume = fields.Float()
    ratio = fields.Char()
    ratio_type = fields.Selection([('higher', 'Higher'), ('lower', 'Lower'), ('accurate', 'Accurate')], default=None)
    uom_id = fields.Many2one('uom.uom')
