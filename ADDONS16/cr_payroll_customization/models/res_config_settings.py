# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account', related='company_id.analytic_account_id', store=True,
        readonly=False )
    journal_id = fields.Many2one(comodel_name='account.journal', string='Salary Journal', related='company_id.journal_id', store=True,
        readonly=False )



class ResCompany(models.Model):
    _inherit = "res.company"

    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account' )
    journal_id = fields.Many2one(comodel_name='account.journal', string='Salary Journal')
    

