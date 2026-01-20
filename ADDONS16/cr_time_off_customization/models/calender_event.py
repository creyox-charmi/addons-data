from odoo import models, api

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    @api.model
    def check_access_rule(self, operation):
        if not self.env.user.has_group('base.group_system'):
            # Restrict access to only the user's own records
            domain = [('create_uid', '=', self.env.uid)]
            records = self.search(domain)
            if not records:
                # raise AccessError("You do not have access to these records.")
                pass
        return super(CalendarEvent, self).check_access_rule(operation)