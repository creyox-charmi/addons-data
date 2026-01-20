from tokenize import String

import werkzeug.exceptions
import werkzeug.urls
from lxml.doctestcompare import strip

from werkzeug.urls import url_parse

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import unslug_url
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.translate import html_translate


class Customer(models.Model):

    _name = "cr.customer"
    _description = "Customer"

    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    email = fields.Char(string='E-mail')
    phone_no = fields.Char(string='Phone no')
    country_id = fields.Many2one('res.country',string="Country")
    state_id = fields.Many2one('res.country.state',string="State")
    city = fields.Char(string='City')
    zip = fields.Char(string='Zip Code')
    address = fields.Char(string='Address')
