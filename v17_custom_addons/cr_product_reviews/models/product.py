from odoo import api, fields, models, _

class Product(models.Model):
    _name = 'product'

    name = fields.Char(string="name")
    price = fields.Integer(string="price")
    review_id = fields.One2many(string="review_id",
                                comodel_name='product.review',
                                inverse_name='product_id')
    no_of_review = fields.Integer(string="no_of_trainner", compute="_compute_no_of_review", store=True)

    @api.depends('review_id')
    def _compute_no_of_review(self):
        for record in self:
            record.no_of_review = len(record.review_id)


    def action_get_record(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'product.wizard',
            'views': [(False, 'form')],
            'target': 'new',
        }
    def action_get_review_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Review',
            'view_mode': 'tree,form',
            'domain':[('product_id','=',self.id)],
            'res_model': 'product.review',
        }
