from odoo import models, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        self = self.with_context(tracking_disable=True, mail_notrack=True, mail_create_nolog=True)
        leads = super(CrmLead, self).create(vals_list)
        return leads