from odoo import api, Command, fields, models, SUPERUSER_ID, _


class Stock(models.Model):
    _inherit = 'stock.picking'

    # def create(self, vals_list):
    #     res = super(Stock, self).create(vals_list)
    #     print("res : ",res)
    #     print('vals_list : ',vals_list)
    #     print("yes confirm")
    #     po = vals_list['origin']
    #     if po:
    #         print(res.move_ids_without_package)
    #         # res.button_validate()
    #
    #     return res

    # def action_confirm(self):
    #     res = super(Stock, self).action_confirm()
    #     print("res : ",res)
    #     return res
