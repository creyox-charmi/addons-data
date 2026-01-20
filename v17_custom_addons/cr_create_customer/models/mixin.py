from itertools import product

from odoo import api, fields, models



class WebsiteSearchableMixin(models.AbstractModel):
    _inherit = 'website.searchable.mixin'

    def _search_fetch(self, search_detail, search, limit, order):
        model = self.sudo() if search_detail.get('requires_sudo') else self

        model_name = self.env['product.template']
        if model == model_name:
            print("yessssssssssssssssss")
            product_ids = self.env['product.template'].search(
                [
                    ('categ_id', 'in', self.env.user.cr_product_category_ids.ids)
                ]
            )
            domain = [('id', 'in', product_ids.ids)]
            default_domain = search_detail['base_domain']
            default_domain.append(domain)

        res = super(WebsiteSearchableMixin, self)._search_fetch(search_detail, search, limit, order)

        return res



