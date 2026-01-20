# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import werkzeug.urls
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class Event(models.Model):
    _name = 'event.event'
    _inherit = [
        'event.event',
        'website.seo.metadata',
        'website.published.multi.mixin',
        'website.cover_properties.mixin',
        'website.searchable.mixin',
    ]

    website_visibility = fields.Selection(
        [('public', 'Public'), ('link', 'Via a Link'), ('logged_users', 'Logged Users')],
        string="Website Visibility", required=True, default='public', tracking=True,
        help="""Defines the Visibility of the Event on the Website and searches.\n
            Note that the Event is however always available via its link.""")

    is_visible_on_website = fields.Boolean(string="Visible On Website", compute='_compute_is_visible_on_website', search='_search_is_visible_on_website')
    is_participating = fields.Boolean(
        "Is Participating",
        compute="_compute_is_participating",
        search="_search_is_participating"
    )
    event_register_url = fields.Char('Event Registration Link', compute='_compute_event_register_url')


    @api.depends_context('uid')
    @api.depends('website_visibility', 'is_participating')
    def _compute_is_visible_on_website(self):
        print("_compute_is_visible_on_website....")
        if all(event.website_visibility == 'public' for event in self):
            self.is_visible_on_website = True
            return
        for event in self:
            if event.website_visibility == 'public' or event.is_participating:
                event.is_visible_on_website = True
            elif not self.env.user._is_public() and event.website_visibility == 'logged_users':
                event.is_visible_on_website = True
            else:
                event.is_visible_on_website = False

    @api.model
    def _search_is_visible_on_website(self, operator, value):
        print("_search_is_visible_on_website....")
        if operator not in ['=', '!=']:
            raise NotImplementedError(_('This operator is not supported'))
        if not isinstance(value, bool):
            raise UserError(_('Value should be True or False (not %)', value))
        check_is_visible_on_website = operator == '=' and value or operator == '!=' and not value
        user = self.env.user
        domain = [('is_participating', '=', True)]

        if not user._is_public():
            domain = expression.OR([domain, [('website_visibility', 'in', ['public', 'logged_users'])]])
        else:
            domain = expression.OR([domain, [('website_visibility', '=', 'public')]])

        event_ids = self.env['event.event']._search(domain)
        return [('id', 'in' if check_is_visible_on_website else 'not in', event_ids)]

    @api.model
    def _search_get_detail(self, website, order, options):
        print("_search_get_detail....")
        # Call the parent method to get the original result
        result = super(Event,self)._search_get_detail(website, order, options)

        # Add your additional domain condition
        result['base_domain'].append([('is_visible_on_website', '=', True)])
        result['no_date_domain'].append([('is_visible_on_website', '=', True)])
        result['no_country_domain'].append([('is_visible_on_website', '=', True)])

        return result


    @api.model
    def _search_is_participating(self, operator, value):
        if operator not in ['=', '!=']:
            raise NotImplementedError(_('This operator is not supported'))
        if not isinstance(value, bool):
            raise UserError(_('Value should be True or False (not %)', value))
        check_is_participating = operator == '=' and value or operator == '!=' and not value

        return [('id', 'in' if check_is_participating else 'not in', self._fetch_is_participating_events().ids)]

    @api.model
    def _fetch_is_participating_events(self):
        """Heuristic

          * public, no visitor: not participating as we have no information;
          * check only confirmed and attended registrations, a draft registration
            does not make the attendee participating;
          * public and visitor: check visitor is linked to a registration. As
            visitors are merged on the top parent, current visitor check is
            sufficient even for successive visits;
          * logged, no visitor: check partner is linked to a registration. Do
            not check the email as it is not really secure;
          * logged as visitor: check partner or visitor are linked to a
            registration;
        """
        current_visitor = self.env['website.visitor']._get_visitor_from_request()
        if self.env.user._is_public() and not current_visitor:
            return self.env['event.event']

        base_domain = [('state', 'in', ['open', 'done'])]
        if self:
            base_domain = expression.AND([[('event_id', 'in', self.ids)], base_domain])

        visitor_domain = []
        partner_id = self.env.user.partner_id
        if current_visitor:
            visitor_domain = [('visitor_id', '=', current_visitor.id)]
            partner_id = current_visitor.partner_id
        if partner_id:
            visitor_domain = expression.OR([visitor_domain, [('partner_id', '=', partner_id.id)]])

        registrations_events = self.env['event.registration'].sudo()._read_group(
            expression.AND([visitor_domain, base_domain]),
            ['event_id'], ['__count'])
        return self.env['event.event'].browse([event.id for event, _reg_count in registrations_events])

    # @api.depends('website_url')
    # def _compute_event_register_url(self):
    #     for event in self:
    #         event.event_register_url = werkzeug.urls.url_join(event.get_base_url(), f"{event.website_url}/register")

    @api.depends('website_url', 'website_visibility')
    def _compute_event_register_url(self):
        for event in self:
            base_url = event.get_base_url()
            event_url = werkzeug.urls.url_join(base_url, f"{event.website_url}/register")

            # If the event is restricted to logged-in users, append a security flag
            if event.website_visibility == 'logged_users':
                print("yessss")
                event_url += "?auth_required=true"

            event.event_register_url = event_url
