from odoo import api, fields, models



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False):
    #     user = self.env.user
    #
    #     product_ids = user.cr_product_ids.ids
    #     if product_ids:
    #         args.append(("id", "in", product_ids))
    #         print(args)
    #
    #     return super(ProductTemplate, self)._search(args, offset, limit, order, count)

