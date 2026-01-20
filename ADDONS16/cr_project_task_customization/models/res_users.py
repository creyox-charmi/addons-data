from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    is_freelancer = fields.Boolean(string="Is Freelancer?")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        current_user = self.env.user
        args = args or []

        if not current_user.has_group('base.group_system'):
            args.append(('id', '=', current_user.id))

        return super(ResUsers, self).name_search(name=name, args=args, operator=operator, limit=limit)