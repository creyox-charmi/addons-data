from odoo import api, fields, models, _
from datetime import datetime


class Employee(models.Model):
    """_name is display in the url when we are open department(table) of models(database) """
    _name = 'cr.employee.employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_names_search = ['birthdate', 'name','mobile','email']


    """below all fields are the column of the table department"""
    name = fields.Char(string="name")
    image = fields.Binary(string="image")
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
    job_time = fields.Selection(
        [
            ('full_time', "Full_time"),
            ('part_time', 'Part_time')
        ],
        string="job_time"
    )
    notes = fields.Html(string="notes")
    remarks = fields.Text(string="remarks")
    is_hod = fields.Boolean(string="is_hod")
    active = fields.Boolean(string="active")

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

    """we can only apply this function on Many2one field."""
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, order=None):
        print("Function call _name_search")
        args = args or []
        domain = []
        if name:
            domain = ['|', '|',
                      ('name', operator, name),
                      ('email', operator, name),
                      ('mobile', operator, name)
                      ]
        return self._search(domain + args, limit=limit, order=order)

    """we can only apply this function on Many2one field."""
    @api.depends('name', 'birthdate','job_time')
    def _compute_display_name(self):
        for rec in self:
            if rec.name and rec.birthdate and rec.job_time:
                rec.display_name = f"{rec.name} | {rec.birthdate} | {rec.job_time}"
            else:
                rec.display_name = f"{rec.name}"