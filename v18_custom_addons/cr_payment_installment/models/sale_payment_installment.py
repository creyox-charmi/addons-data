# -*- coding: utf-8 -*-
# Part of Creyox technologies.
from odoo import api, fields, models, _


class CrSaleInstallmentLine(models.Model):
    _name = "cr.sale.installment.line"
    _description = "Sale Installment Line"
    _order = "payment_date"
    _rec_name = "description"

    amount = fields.Float(string="Amount")
    index = fields.Integer(string="No")
    sale_id = fields.Many2one("sale.order", "Sale Order", ondelete="cascade")
    payment_date = fields.Date(string="payment Date")
    description = fields.Char(string="Description")
    state = fields.Selection(
        [("draft", "Draft"), ("paid", "Paid")], default="draft", string="Status"
    )
