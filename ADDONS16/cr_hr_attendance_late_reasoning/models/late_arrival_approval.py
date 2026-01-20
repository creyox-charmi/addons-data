from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class LateArrivalApproval(models.Model):
    _name = 'late.arrival.approval'
    _description = 'details of employee on how many times he/she has come late'
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    month = fields.Selection(
        selection=[
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
        ],
        string="Month",
        required=True
    )
    year = fields.Char(string='Year')
    late_check_in_count  = fields.Integer('No.of Late Arrivals', compute='compute_late_check_in_count')
    approval_btn_show = fields.Boolean(default=True, compute='compute_approval_btn_show')
    approved_already = fields.Boolean(default=False)
    
    @api.depends('late_check_in_count')
    def compute_approval_btn_show(self):
        '''the function is responsible for visiblity of the approval button and pop box'''
        
        for rec in self:
            if rec.employee_id.resource_calendar_id.late_allowance_times <= rec.late_check_in_count and not rec.approved_already:
                rec.employee_id.write({
                    'is_late_arrival_limit_crossed': True,
                })
                rec.approval_btn_show = True
            else:
                rec.employee_id.write({
                    'is_late_arrival_limit_crossed': False,
                })
                rec.approval_btn_show = False
    
    def compute_late_check_in_count(self):
        '''counts the number of times user has come late in current month'''

        for employee in self:
            # Fetch the current date and calculate the first and last day of the current month
            
            month = int(employee.month)
            today = datetime.now().replace(month=month)
            first_day = today.replace(day=1)
            last_day = (today.replace(day=1) + relativedelta(months=1)) - relativedelta(days=1)
            
            lates = self.env['hr.attendance'].search([('late_reason','!=', False),('employee_id','=', self.employee_id.id), ('check_in', '>=', first_day), ('check_out', '<=', last_day)])
            count = 0
            for late in lates:
                count+=1
            employee.late_check_in_count = count
                
    def action_approve(self):
        '''approve the late arrival'''
        self.write({'approved_already':True, 'approval_btn_show': False })
        self.employee_id.write({
            'is_late_arrival_limit_crossed': False,
        })
        
    
    
