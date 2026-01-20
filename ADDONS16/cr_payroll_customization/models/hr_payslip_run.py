from odoo import fields, models
from dateutil.relativedelta import relativedelta


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"
    
    def _default_date_start(self):
        """Default start date: Start of the next month based on the latest record."""
        latest_record = self.search([], order="date_end desc", limit=1)
        if latest_record and latest_record.date_end:
            # Calculate start date of the next month
            return (latest_record.date_end + relativedelta(months=1, day=1))
        else:
            # Default to the start of the current month if no previous record exists
            return fields.Date.today().replace(day=1)
    
    def _default_date_end(self):
        """Default end date: End of the next month based on the start date."""
        start_date = self._default_date_start()
        return start_date + relativedelta(day=31)
    
    analytic_account_id = fields.Many2one(
        "account.analytic.account", 
        default=lambda self: self.env.user.company_id.analytic_account_id.id 
        if self.env.user.company_id.analytic_account_id else False
    )
    
    journal_id = fields.Many2one(
        'account.journal', 
        'Salary Journal', 
        readonly=True, 
        required=True,
        states={'draft': [('readonly', False)]}, 
        default=lambda self: self.env.user.company_id.journal_id.id 
        if self.env.user.company_id.journal_id else False
    )
    
    date_start = fields.Date(
        string='Date From', 
        required=True, 
        readonly=True,
        states={'draft': [('readonly', False)]}, 
        default=_default_date_start
    )
    
    date_end = fields.Date(
        string='Date To', 
        required=True, 
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=_default_date_end
    )
