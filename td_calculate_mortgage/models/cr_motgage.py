# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Mortgage(models.Model):
    _name = "cr.mortgage"
    _description = "Mortgage"

    name = fields.Char(string="Client Name")
    email = fields.Char(string="E-mail")
    number = fields.Char(string="Phone")
    province = fields.Char(string="Province")
    work_since = fields.Selection(string="Work since",
                             selection=[
                                 ('1', "Less than 12 months"),
                                 ('2', "Between 1 year y 2 years"),
                                 ('3', "More than 2 years"),
                             ]
                             )
    situation = fields.Selection(string="Situation",
                                 selection = [
                                     ('1', "I have already decided on the house"),
                                     ('2', "I am looking for housing"),
                                     ('3', "I'm just looking for information"),
                                 ]
                                 )
    situation_province = fields.Char(string="Situation Province")
    type_of_home = fields.Selection(string='Type of Home',
                                    selection=[
                                        ('Primera', "First home"),
                                        ('Segundavivienda', "Second home"),
                                        ('Autompromocion', "Self-promotion"),
                                        ('Refinanciación', "Refinancing"),
                                        ('Otros', "Others"),
                                    ]
                                    )
    value_of_house = fields.Char(string='Value Of House')
    saved_money = fields.Char(string='Saved Money')
    mortgage_year = fields.Integer(string='Mortgage Year')
    shopping = fields.Selection(string="Shopping",
                                 selection = [
                                     ('1', "I am the sole holder of the mortgage"),
                                     ('2', "My mortgage has two holders"),
                                 ]
                                 )
    monthly_net_income = fields.Selection(string="Monthly Net Income",
                                 selection = [
                                     ('1', "Less than €1,500"),
                                     ('2', "Between €1,500 and €2,200"),
                                     ('3', "More than €2,200"),
                                     ('4', "Less than €2,400"),
                                     ('5', "Between €2,400 and €3,500"),
                                     ('6', "More than €3,500"),
                                 ]
                                 )
    spent_on_loans_and_card_usage1 = fields.Selection(string="Spent On Loans and Card Usage",
                                 selection = [
                                     ('1', "Less than €200"),
                                     ('2', "From €200 to €500"),
                                     ('3', "More than €500"),
                                 ]
                                 )
    spent_on_loans_and_card_usage2 = fields.Selection(string="Spent On Loans and Card Usage HEADLINE-2",
                                 selection = [
                                     ('1', "Less than €200"),
                                     ('2', "From €200 to €500"),
                                     ('3', "More than €500"),
                                 ],
                                 domain="[('shopping', '=', '2')]"
                                 )