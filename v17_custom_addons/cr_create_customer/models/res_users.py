from odoo import api, fields, models



class User(models.Model):
    _inherit = 'res.users'

    cr_product_ids = fields.Many2many(comodel_name='product.template',
                                      string='Products')
    cr_product_category_ids = fields.Many2many(comodel_name='product.category',
                                      string='Product Category')


    # @api.onchange('cr_product_ids')
    # def set_limit(self):
    #     """Method to set the sale order limit on stock picking actions"""
    #     for record in self:
    #         print("callllllllllllllllllll")
    #         actions = record.env["ir.actions.act_window"].search(
    #             [
    #                 ("name", "=", "Product Pages"),
    #                 ("res_model", "=", "product.template"),
    #                 ("target", "=", "current"),
    #                 ("type", "=", "ir.actions.act_window"),
    #             ]
    #         )
    #         if actions:
    #             for action in actions:
    #                 domain = [('id', 'in', self.env.user.cr_product_ids.ids)]
    #                 action.write({"domain": domain})
    #                 print(actions.domain)





