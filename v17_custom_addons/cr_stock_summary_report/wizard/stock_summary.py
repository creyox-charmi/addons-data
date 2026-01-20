from datetime import date
from operator import truediv

from odoo import fields, models


class StockSummary(models.TransientModel):
    _name = 'cr.stock.summary'
    _description = 'Stock Summary'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    product_variants_ids = fields.Many2many(comodel_name = 'product.product',string='Product')

    def cr_print_report(self):
        print("enter")
        for record in self.product_variants_ids:
            st = self.env['stock.move'].search(
                [
                    ('product_id','=',record.id),
                ]
            )
            print(st)

            dict = []
            date_start = self.start_date.strftime('%Y-%m-%d')
            print(date_start)
            for move in st:
                date_compare = move.date.date()


                if date_start == date_compare:
                    print(move)
                    dict.append(move)

            print(dict)




    def discard(self):
        return True



