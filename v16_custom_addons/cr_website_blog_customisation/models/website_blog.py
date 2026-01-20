# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models
import random

class BlogPost(models.Model):
    _inherit = "blog.post"

    color = fields.Many2one(comodel_name='color.management', string="Background color", widget="color")
    background_color = fields.Char(related='color.color_code')

    @api.model
    def create(self, vals):
        # Fetch all colors from the 'color.management' model
        colors = self.env['color.management'].search([])

        # If there are colors in the database, pick a random one
        if colors:
            random_color = random.choice(colors)
            # Set the random color's ID to the 'color' field
            vals['color'] = random_color.id
            vals['background_color'] = random_color.color_code
            print("Random color selected: ", random_color.name, "Hex Code: ", random_color.color_code)

        # Call the original create method to create the record
        return super(BlogPost, self).create(vals)


class BlogTag(models.Model):
    _inherit = 'blog.tag'

    active = fields.Boolean(string="Active")

