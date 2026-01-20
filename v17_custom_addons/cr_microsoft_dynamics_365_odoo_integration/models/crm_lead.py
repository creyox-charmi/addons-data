# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_dynamics_lead_id = fields.Char('Dynamics Lead ID', index=True, help="Unique identifier from Dynamics 365")
    x_dynamics_opportunity_id = fields.Char(
        string='Dynamics Opportunity ID',
        help='Unique identifier from Dynamics 365 Opportunity',
        index=True
    )
    x_budget_amount = fields.Float(
        string='Budget Amount',
        help='Budget amount from Dynamics 365 Opportunity'
    )
    x_actual_value = fields.Float(
        string='Actual Value',
        help='Actual closed value from Dynamics 365 Opportunity'
    )