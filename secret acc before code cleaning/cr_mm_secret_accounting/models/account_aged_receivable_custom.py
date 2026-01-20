from odoo import api, models, _, fields
import logging

_logger = logging.getLogger(__name__)
# ------------------------------
# Aged Receivable Custom Report
# ------------------------------
class AgedReceivableCustom(models.AbstractModel):
    _name = "account.aged.receivable.custom"
    _description = "Aged Receivable (Custom)"
    _inherit = "account.aged.receivable.report.handler"

    # def _get_aml_values(self, options, partner_ids=None, offset=0, limit=None):
    #     aml_values = super()._get_aml_values(options, partner_ids, offset=offset, limit=limit)
    #     return self.env["account.report.secret.mixin"]._filter_secret_amls(aml_values)