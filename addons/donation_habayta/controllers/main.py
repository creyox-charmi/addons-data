from odoo import http, models, fields, _
from odoo.addons.portal.controllers.web import Home
from odoo.fields import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.tools.json import scriptsafe as json_safe
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
import logging
from odoo import http, _
from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.http import request
from odoo.tools.json import scriptsafe as json_safe
from odoo.tools.translate import LazyTranslate
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from odoo.addons.account_payment.controllers import portal as account_payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
_lt = LazyTranslate(__name__)

_logger = logging.getLogger(__name__)
class PaymentPortal(payment_portal.PaymentPortal):

    @http.route('/donation/pay', type='http', methods=['GET', 'POST'], auth='public', website=True, sitemap=False,
                list_as_website_content=_lt("Donation Payment"))
    def donation_pay(self, **kwargs):
        """ Behaves like PaymentPortal.payment_pay but for donation

        :param dict kwargs: As the parameters of in payment_pay, with the additional:
            - str donation_options: The options settled in the donation snippet
            - str donation_descriptions: The descriptions for all prefilled amounts
        :return: The rendered donation form
        :rtype: str
        :raise: werkzeug.exceptions.NotFound if the access token is invalid
        """
        kwargs['utm_campaign_id'] = kwargs.get('utm_campaign_id')
        kwargs['utm_source_id'] = kwargs.get('utm_source_id')
        kwargs['utm_medium_id'] = kwargs.get('utm_medium_id')

        kwargs['is_donation'] = True
        kwargs['currency_id'] = self._cast_as_int(kwargs.get('currency_id')) or request.env.company.currency_id.id
        kwargs['amount'] = self._cast_as_float(kwargs.get('amount')) or 25.0
        kwargs['donation_options'] = kwargs.get('donation_options', json_safe.dumps(dict(customAmount="freeAmount")))

        if request.env.user._is_public():
            kwargs['partner_id'] = request.env.user.partner_id.id
            kwargs['access_token'] = payment_utils.generate_access_token(kwargs['partner_id'], kwargs['amount'],
                                                                         kwargs['currency_id'])
        return self.payment_pay(**kwargs)


    @http.route('/payment/transaction', type='jsonrpc', auth='public')
    def payment_transaction(self, amount, currency_id, partner_id, access_token,
                            provider_id=None, payment_method_id=None, token_id=None,
                            flow=None, tokenization_requested=None, landing_route=None,
                            **kwargs):
        """Override to capture and pass UTM values to transaction creation"""


        # Extract UTM values from partner_details (they're nested there from JS)
        partner_details = kwargs.get('partner_details', {})
        utm_campaign_id = partner_details.get('utm_campaign_id', '')
        utm_source_id = partner_details.get('utm_source_id', '')
        utm_medium_id = partner_details.get('utm_medium_id', '')

        # Put UTM values at root level of kwargs for _create_transaction
        kwargs.update({
            'utm_campaign_id': utm_campaign_id,
            'utm_source_id': utm_source_id,
            'utm_medium_id': utm_medium_id,
        })

        # Call parent method with updated kwargs
        return super().payment_transaction(amount, currency_id, partner_id, access_token, **kwargs)


    def _create_transaction(
            self, provider_id, payment_method_id, token_id, amount, currency_id, partner_id, flow,
            tokenization_requested, landing_route, reference_prefix=None, is_validation=False,
            custom_create_values=None, **kwargs
    ):
        """Override to convert UTM string values to IDs"""

        # Get UTM values from kwargs
        utm_campaign_name = kwargs.get('utm_campaign_id', '')
        utm_source_name = kwargs.get('utm_source_id', '')
        utm_medium_name = kwargs.get('utm_medium_id', '')


        # Convert string names to IDs (or create if they don't exist)
        utm_campaign_id = None
        utm_source_id = None
        utm_medium_id = None

        if utm_campaign_name:
            campaign = request.env['utm.campaign'].sudo().search([
                ('name', '=', utm_campaign_name)
            ], limit=1)
            if not campaign:
                campaign = request.env['utm.campaign'].sudo().create({
                    'name': utm_campaign_name
                })
            utm_campaign_id = campaign.id

        if utm_source_name:
            source = request.env['utm.source'].sudo().search([
                ('name', '=', utm_source_name)
            ], limit=1)
            if not source:
                source = request.env['utm.source'].sudo().create({
                    'name': utm_source_name
                })
            utm_source_id = source.id

        if utm_medium_name:
            medium = request.env['utm.medium'].sudo().search([
                ('name', '=', utm_medium_name)
            ], limit=1)
            if not medium:
                medium = request.env['utm.medium'].sudo().create({
                    'name': utm_medium_name
                })
            utm_medium_id = medium.id

        # Rest of your existing code...
        provider_sudo = request.env['payment.provider'].sudo().browse(provider_id)
        tokenize = False
        if flow in ['redirect', 'direct']:
            payment_method_sudo = request.env['payment.method'].sudo().browse(payment_method_id)
            token_id = None
            tokenize = bool(
                provider_sudo.allow_tokenization
                and payment_method_sudo.support_tokenization
                and (provider_sudo._is_tokenization_required(**kwargs) or tokenization_requested)
            )
        elif flow == 'token':
            token_sudo = request.env['payment.token'].sudo().browse(token_id)
            partner_sudo = request.env['res.partner'].sudo().browse(partner_id)
            if partner_sudo.commercial_partner_id != token_sudo.partner_id.commercial_partner_id:
                raise AccessError(_("You do not have access to this payment token."))
            payment_method_id = token_sudo.payment_method_id.id

        reference = request.env['payment.transaction']._compute_reference(
            provider_sudo.code,
            prefix=reference_prefix,
            **(custom_create_values or {}),
            **kwargs
        )

        if is_validation:
            amount = provider_sudo._get_validation_amount()
            payment_method = request.env['payment.method'].browse(payment_method_id)
            currency_id = provider_sudo.with_context(
                validation_pm=payment_method
            )._get_validation_currency().id

        # Create the transaction with INTEGER IDs instead of string names
        tx_sudo = request.env['payment.transaction'].sudo().create({
            'provider_id': provider_sudo.id,
            'payment_method_id': payment_method_id,
            'reference': reference,
            'amount': amount,
            'currency_id': currency_id,
            'partner_id': partner_id,
            'token_id': token_id,
            'operation': f'online_{flow}' if not is_validation else 'validation',
            'tokenize': tokenize,
            'landing_route': landing_route,
            'utm_campaign_id': utm_campaign_id,  # Now it's an integer ID
            'utm_source_id': utm_source_id,  # Now it's an integer ID
            'utm_medium_id': utm_medium_id,  # Now it's an integer ID
            **(custom_create_values or {}),
        })

        if flow != 'token':
            tx_sudo._log_sent_message()
        elif not request.env.context.get('delay_token_charge'):
            tx_sudo._charge_with_token()

        PaymentPostProcessing.monitor_transaction(tx_sudo)

        return tx_sudo


    def _get_custom_rendering_context_values(self, donation_options=None, donation_descriptions=None, is_donation=False,
                                             **kwargs):
        rendering_context = super()._get_custom_rendering_context_values(**kwargs)
        if is_donation:
            user_sudo = request.env.user
            logged_in = not user_sudo._is_public()
            partner_sudo = user_sudo.partner_id
            partner_details = {}
            countries = request.env['res.country']
            if logged_in:
                partner_details = {
                    'name': partner_sudo.name,
                    'email': partner_sudo.email,
                    'country_id': partner_sudo.country_id.id,
                }

            countries = request.env['res.country'].sudo().search([])
            descriptions = request.httprequest.form.getlist('donation_descriptions')

            donation_options = json_safe.loads(donation_options) if donation_options else {}
            donation_amounts = json_safe.loads(donation_options.get('donationAmounts', '[]'))

            rendering_context.update({
                'is_donation': True,
                'partner': partner_sudo,
                'transaction_route': '/donation/transaction/%s' % donation_options.get('minimumAmount', 0),
                'partner_details': partner_details,
                'error': {},
                'countries': countries,
                'donation_options': donation_options,
                'donation_amounts': donation_amounts,
                'donation_descriptions': descriptions,
                'utm_campaign_id': request.session.get('utm_campaign_id', ''),
                'utm_source_id': request.session.get('utm_source_id', ''),
                'utm_medium_id': request.session.get('utm_medium_id', ''),
            })
        return rendering_context


    def _get_extra_payment_form_values(
            self,
            donation_options=None,
            donation_descriptions=None,
            is_donation=False,
            utm_campaign_id=None,  # Add your custom parameters here
            utm_source_id=None,  # Add your custom parameters here
            utm_medium_id=None,  # Add your custom parameters here
            **kwargs
    ):
        """Override to add UTM tracking values to the payment form context"""

        # Call parent method
        rendering_context = super()._get_extra_payment_form_values(
            donation_options=donation_options,
            donation_descriptions=donation_descriptions,
            is_donation=is_donation,
            utm_campaign_id=utm_campaign_id,
            utm_source_id=utm_source_id,
            utm_medium_id=utm_medium_id,
            **kwargs,
        )

        # Add UTM values to rendering context if this is a donation
        if is_donation:
            rendering_context.update({
                'utm_campaign_id': utm_campaign_id or '',
                'utm_source_id': utm_source_id or '',
                'utm_medium_id': utm_medium_id or '',
            })

        return rendering_context


    @http.route('/donation/transaction/<minimum_amount>', type='jsonrpc', auth='public', website=True, sitemap=False)
    def donation_transaction(self, amount, currency_id, partner_id, access_token, minimum_amount=0, **kwargs):
        """Override to extract and pass UTM values from partner_details"""

        # Extract UTM values from partner_details (they're nested there from JS)
        partner_details = kwargs.get('partner_details', {})
        utm_campaign_id = partner_details.get('utm_campaign_id', '')
        utm_source_id = partner_details.get('utm_source_id', '')
        utm_medium_id = partner_details.get('utm_medium_id', '')


        # Validate minimum amount
        if float(amount) < float(minimum_amount):
            raise ValidationError(_('Donation amount must be at least %.2f.', float(minimum_amount)))

        use_public_partner = request.env.user._is_public() or not partner_id
        if use_public_partner:
            details = kwargs['partner_details']
            if not details.get('name'):
                raise ValidationError(_('Name is required.'))
            if not details.get('email'):
                raise ValidationError(_('Email is required.'))
            if not details.get('country_id'):
                raise ValidationError(_('Country is required.'))
            partner_id = request.website.user_id.partner_id.id
            del kwargs['partner_details']
        else:
            partner_id = request.env.user.partner_id.id

        # ✅ ADD UTM FIELDS TO WHITELIST
        self._validate_transaction_kwargs(kwargs, additional_allowed_keys=(
            'donation_comment', 'donation_recipient_email', 'partner_details', 'reference_prefix',
            'utm_campaign_id', 'utm_source_id', 'utm_medium_id'  # ← Add these
        ))

        if use_public_partner:
            kwargs['custom_create_values'] = {'tokenize': False}

        # Add UTM values to kwargs for _create_transaction
        kwargs.update({
            'utm_campaign_id': utm_campaign_id,
            'utm_source_id': utm_source_id,
            'utm_medium_id': utm_medium_id,
        })

        tx_sudo = self._create_transaction(
            amount=amount, currency_id=currency_id, partner_id=partner_id, **kwargs
        )

        tx_sudo.is_donation = True
        if use_public_partner:
            tx_sudo.update({
                'partner_name': details['name'],
                'partner_email': details['email'],
                'partner_country_id': int(details['country_id']),
            })
        elif not tx_sudo.partner_country_id:
            tx_sudo.partner_country_id = int(kwargs.get('partner_details', {}).get('country_id', 0))

        # Recompute access token
        access_token = payment_utils.generate_access_token(
            tx_sudo.partner_id.id, tx_sudo.amount, tx_sudo.currency_id.id
        )
        self._update_landing_route(tx_sudo, access_token)

        # Send donation email
        recipient_email = kwargs.get('donation_recipient_email', '')
        comment = kwargs.get('donation_comment', '')
        tx_sudo._send_donation_email(True, comment, recipient_email)

        return tx_sudo._get_processing_values()


