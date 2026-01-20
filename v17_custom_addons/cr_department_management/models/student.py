from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from datetime import datetime


class Student(models.Model):
    """_name is display in the url when we are open department(table) of models(database) """
    _name = 'cr.student.student'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    """below all fields are the column of the table department"""
    name = fields.Char(string="name")
    image = fields.Binary(string="image")
    custom_inf = fields.Char(string="Custom Inf", compute='_compute_custom_inf')
    street = fields.Char(string="street")
    city = fields.Char(string="city")
    zip = fields.Char(string="zip")
    state_id = fields.Many2one('res.country.state',
                               string="state_id")
    country_id = fields.Many2one('res.country',
                                 string="country_id")
    birthdate = fields.Date(string="birthdate")
    age = fields.Float(string="age",
                       compute='_compute_age',
                       store=True)
    mobile = fields.Char(string="mobile")
    email = fields.Char(string="email")
    barcode = fields.Char(string="barcode")
    department_id = fields.Many2one(comodel_name='cr.department.department',
                                    string="department_id")
    """here dept_code is related with the 'code' field of the cr.department.department
       the data type of the both related field are must be the same"""
    dept_code = fields.Char(string="dept_code", related="department_id.code", store=True)
    type = fields.Selection(
        [
            ('internal', 'Internal'),
            ('external', 'External')
        ],
        string="type"
    )
    notes = fields.Html(string="notes")
    remarks = fields.Text(string="remarks")
    is_cr = fields.Boolean(string="is_cr")
    cr_start_date = fields.Date(string="cr_start_date ")
    cr_end_date = fields.Date(string="cr_end_date")
    no_of_votes = fields.Integer(string="no_of_votes")
    active = fields.Boolean(string="active")

    def _compute_custom_inf(self):
        for record in self:
            record.custom_inf = record.id

    @api.onchange('mobile')
    def _onchange_mobile(self):
        self.barcode = self.mobile

    @api.depends('birthdate')
    def _compute_age(self):
        today = datetime.today()
        for student in self:
            if student.birthdate:
                birthdate = fields.Date.from_string(student.birthdate)
                age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
                student.age = age
            else:
                student.age = 0

    @api.constrains('mobile')
    def _check_mobile_fields(self):
        for record in self:
            if len(record.mobile) != 10:
                raise ValidationError("Invalid mobile!")


    @api.constrains('cr_start_date', 'cr_end_date', 'no_of_votes', 'is_cr')
    def _check_required_fields(self):
        for record in self:
            if record.is_cr:
                if not record.cr_start_date:
                    raise ValidationError("CR Start Date must be filled if 'Is CR' is True.")
                if not record.cr_end_date :
                    raise ValidationError("CR End Date must be filled if 'Is CR' is True.")
                if record.no_of_votes is None or record.no_of_votes <= 0:
                    raise ValidationError("No of Votes must be greater than 0 if 'Is CR' is True.")

