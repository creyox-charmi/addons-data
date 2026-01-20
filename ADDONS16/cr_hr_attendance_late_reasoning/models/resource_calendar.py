from odoo import models, fields


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    check_in_delay_allowance = fields.Float(string="Check-in Delay Allowance", help='Consider format HH:MM')
    late_allowance_times = fields.Integer(string="Late Allowance Limit per Month", help='How many times the person should be allowed to come late', default=1)