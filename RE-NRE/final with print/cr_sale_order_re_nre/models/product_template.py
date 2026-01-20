from odoo import models, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('name', 'default_code')
    def _compute_display_name(self):
        print('yessssssssss')
        for template in self:
            # Show only product name, ignore default_code
            template.display_name = template.name or ''