# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields,api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _compute_state(self):
        base = super()._compute_state()
        print('super...')
        # print('self : ',self)
        # print('self.picking_type_id : ',self.picking_type_id)
        # print('state : ', self.state)
        for data in self:
            if data.picking_type_id.id == 6:
                print('1..')
                if data.state == 'assigned':
                    print('2..')
                    data.do_unreserve()
                    data.state = 'confirmed'
        return base


    # def do_unreserve(self):
    #     print('call....................')
    #     ref = super().do_unreserve()
    #     print('>>> ',ref)
    #     print(self)
    #     print('>>self.picking_type_id.id  ',self.picking_type_id.id)
    #     print('>>self.state  ', self.state)
    #     if self.picking_type_id.id == 6:
    #         if self.state == 'waiting':
    #             print(">>>>>>>>>>>>>>>>>>>>.")
    #             self.do_unreserve()
    #
    #     return ref

    # def create(self, vals_list):
    #     ref = super(StockPicking, self).create(vals_list)
    #     print('>>',ref ,' -- ',ref.state)
    #     print('>>', ref.picking_type_id)
    #     print('ref.move_ids: ',ref.move_ids)
    #     ref.a()
    #
    #     if ref.picking_type_id.id == 6:
    #         print('yes internal')
    #         ref.do_unreserve()
    #         # print('ref.move_ids')
    #         print('ref.state : ',ref.state)
    #     return ref
    #
    # def a(self):
    #     print(self)
    #     print(self.move_ids)
    #     x= self.env['stock.move'].search([('picking_id','=',self.id)])
    #     print('>>>>>>>>>>>>>>>>>x : ',x)


class Move(models.Model):
    _inherit = "stock.move"

    # def _recompute_state(self):
    #     res = super()._recompute_state()
    #     for move in self:
    #         print('>> move.picking_id',move.picking_id)
    #         print('>> move.id', move.id)
    #         # if move.move_line_ids:
    #         #     for data in move.move_line_ids:
    #         #         print("data : ",data)
    #         if move.id:
    #             if move.picking_id:
    #                 print('>> move.picking_id.picking_type_id.id', move.picking_id.picking_type_id.id)
    #                 if move.picking_id.picking_type_id.id == 6:
    #                     print('>> move.picking_id.state', move.picking_id.state)
    #                     if move.picking_id.state == 'assigned':
    #                         print('>> YESSSS')
    #                         move.picking_id.move_ids._do_unreserve()
    #
    #     return res

    # def _do_unreserve(self):
    #     if self:
    #         ref = super()._do_unreserve()
    #         return ref
    #     else:
    #         return None

    # def create(self, vals_list):
    #     ref = super().create(vals_list)
    #     print('moveeeeeeeeeeeeee')
    #     print('>>',ref)
    #     print('ref.picking_id : ',ref.picking_id)
    #     if ref.picking_id:
    #         print('ref.picking_id.picking_type_id.id : ',ref.picking_id.picking_type_id.id)
    #         if ref.picking_id.picking_type_id.id == 6:
    #             ref.picking_id.do_unreserve()
    #
    #     return ref

class MoveLine(models.Model):
    _inherit = "stock.move.line"

    # def create(self, vals_list):
    #     ref = super().create(vals_list)
    #     # print('vals_list : ', vals_list)
    #     # print('ref : ',ref)
    #     # print('move : ',ref.move_id)
    #     print(ref.move_id.picking_id)
    #     # if ref:
    #     #     if ref.move_id:
    #     #         ref.move_id.picking_id.do_unreserve()
    #     #         # if ref.move_id.picking_id.state == 'waiting':
    #     #         #     ref.move_id.picking_id.state = 'confirmed'
    #
    #     return ref