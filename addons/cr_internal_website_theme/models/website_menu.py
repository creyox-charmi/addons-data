from odoo import models, api


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    @api.model_create_multi
    def create(self, vals_list):
        # Process each menu before creation
        for vals in vals_list:
            # If no parent_id is set and website_id exists
            if not vals.get('parent_id') and vals.get('website_id'):
                # Find the top menu for this website
                top_menu = self.search([
                    ('website_id', '=', vals['website_id']),
                    ('parent_id', '=', False)
                ], limit=1)

                if top_menu:
                    vals['parent_id'] = top_menu.id

        return super(WebsiteMenu, self).create(vals_list)