from odoo import api, models, fields, _
from datetime import datetime


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    name_seq = fields.Char(string='Employee number EPD: ')
    mobile_no = fields.Char(string="Work Mobile", required=True)
    work_no = fields.Char(string="Telephone")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    private_email1 = fields.Char(string="Private Email", readonly=False)
    challenge_id = fields.Many2one('gamification.challenge', string='Employee', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    employee_type = fields.Selection([
        ('employee', "Employee"),
        ("trainee", 'Trainee'),
    ], default='employee', string='Employee Type')
    date_of_birth = fields.Date('Date of Birth', related="birthday", required=True)
    driver_license = fields.Selection([
        ('yes_has_car', 'Yes,has car'),
        ('yes_has_no_car', 'Yes,has no car'),
        ('no', 'No'),
    ], string='Driver License')
    address = fields.Many2one('res.partner', string='Address', related='address_home_id')
    work_locations_main = fields.Many2many('employee.address', 'work_location_red', 'employee_id',
                                           'address_id', string="Work Location")
    work_location_cover = fields.Many2many('employee.address', 'work_location_red', 'employee_id',
                                           'address_id', string="Work Location")
    preferred_location = fields.One2many('employee.address', 'employee_location_id', string="Preferred Location")
    # preferred_location = fields.Selection([
    #     ('amstelveen_&_aalsmeer', 'Amstelveen & Aalsmeer'),
    #     ('iJmond_and_south_kennemerland', 'IJmond and South Kennemerland'),
    #     ('haarlemmermeer', 'Haarlemmermeer'),
    #     ('amsterdam/almere/duo/gooi_en_vecht/utrecht', 'Amsterdam/Almere/DUO/Gooi en Vecht/Utrecht'),
    #     ('zaanstreek-waterland/alkmaar/west_friesland', 'Zaanstreek-Waterland/Alkmaar/West Friesland'),
    #     ('North_east_brabant', 'North east Brabant'),
    #     ('no', 'No'),
    # ], string='Preferred Location', required=True)
    contact_1 = fields.Many2one('hr.employee', string='Contact Person 1')
    contact_2 = fields.Many2one('hr.employee', string='Contact Person 2')
    free_field_1 = fields.Char(string='Free Field 1')
    free_field_42 = fields.Char(string='Free Field 42')
    hours_available = fields.Integer(string='( Hours )available', required=True)
    salary_structure_type = fields.Many2one("hr.payroll.structure.type", related='contract_id.structure_type_id',
                                            string='Salary Structure Type')
    working_hour = fields.Many2one('resource.calendar', string='Working Hours',
                                   related="contract_id.resource_calendar_id")
    hours_balance = fields.Integer(string="Hours Balance +/-", required=True)
    initials = fields.Char(string="Initials")
    residence = fields.Char(string="Residence")
    address_line_2 = fields.Char(string="Address Line 2")
    street = fields.Char(string="Street")
    hours_rate = fields.Integer(string="Hourly Rate")
    postal_code = fields.Char(string="Postal Code")
    start_contract_date = fields.Date('Start Date Contract', related="contract_id.date_start")
    start_pdp_date = fields.Date('Start Date', related='challenge_name.start_date')
    end_pdp_date = fields.Date('End Date', related='challenge_name.end_date')
    end_contract_date = fields.Date('End Date Contract ', related="contract_id.date_end")
    declarability = fields.Char(string='Declarability')
    hour_leave = fields.Integer(string='Hours Of Leave', required=True)
    challenge_name = fields.Many2one('gamification.challenge', string="Challenge Name")
    free_field_3 = fields.Char(string='Free Field 3')
    free_field_4 = fields.Char(string='Free Field 4')
    accreditation_type = fields.Selection([
        ('sjk', "SJK"),
        ("big", 'BIG'),
        ('none_dwant', 'None, do not want'),
        ('none_want-register', 'None, wants to register'),
    ], default='sjk', string='Accreditation Type')
    periodicity = fields.Selection([
        ('once', "Non recurring"),
        ("daily", 'Daily'),
        ("weekly", "Weekly"),
        ("yearly", "Yearly"),
    ], string='periodicity', related='challenge_name.period', readonly=True)
    responsible = fields.Many2one('res.users', string='Responsible', related='challenge_name.manager_id', readonly=True)
    display_mode = fields.Selection([
        ('individual_goal', "Individual Goal"),
        ("leaderboard", 'Leaderboard(Group Ranking)'),
    ], string='Display Mode', related='challenge_name.visibility_mode', readonly=True)
    salutation = fields.Selection([
        ("ms", "MS"),
        ("mr", "MR."),
    ], string='Salutation')
    accr_number = fields.Integer(string='Accr.number', required=True)
    accreditation_exp_date = fields.Date('Accreditation Expiry Date')
    no_of_points = fields.Char(string='Number of points', compute="cal_no_date")
    agb_code = fields.Char(string='AGB Code')
    vog_issue_date = fields.Date('VOG issue Date')
    customer_count = fields.Integer(string='Customer', compute='get_customer_count')
    no_of_points_int = fields.Integer(string='Number of points(NO )')
    no_of_points_date = fields.Date("Number of points(date )")
    free_field_5 = fields.Char(string='Free Field 5')
    free_field_6 = fields.Char(string='Free Field 6')
    free_field_7 = fields.Char(string='Free Field 7')
    free_field_8 = fields.Char(string='Free Field 8')
    free_field_9 = fields.Char(string='Free Field 9')
    free_field_10 = fields.Char(string='Free Field 10')
    free_field_17 = fields.Char(string='Free Field 17')

    # @api.model
    # def create(self, vals_list):
    #     if vals_list.get('name_seq', 'New') == 'New':
    #         vals_list['name_seq'] = self.env['ir.sequence'].next_by_code('Employee.Extension.Sequence') or 'New'
    #     return super(EmployeeInherit, self).create(vals_list)

    def assign_seq(self):
        for rec in self.env['hr.employee'].search([]):
            if rec.name_seq == 'New':
                rec.name_seq = self.env['ir.sequence'].next_by_code('Employee.Extension.Sequence')

    def get_vehicles(self):
        return {
            'name': _('Contacts'),
            'domain': [('emp_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'res.partner',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_customer_count(self):
        count = self.env['res.partner'].search_count([('emp_id', '=', self.id)])
        self.customer_count = count

    @api.depends('no_of_points_int', 'no_of_points_date')
    def cal_no_date(self):
        for rec in self:
            if rec.no_of_points_int and rec.no_of_points_date:
                rec.no_of_points = str(rec.no_of_points_int) + "-" + str(rec.no_of_points_date)
            else:
                rec.no_of_points = None

    # @api.depends('work_locations')
    # def get_work_location(self):
    #     for rec in self:
    #         if rec.work_locations:
    #             rec.work_location = str(rec.work_locations)
    #             # rec.address_id = str(rec.work_locations)
    #         else:
    #             rec.work_location = None


class ContactInherit(models.Model):
    _inherit = 'res.partner'

    emp_id = fields.Many2one('hr.employee', string='Seller', required=False)


class EmployeeAddresses(models.Model):
    _name = 'employee.address'

    name = fields.Char("Location")
    employee_location_id = fields.Many2one('hr.employee', string='Employee', ondelete='cascade')
