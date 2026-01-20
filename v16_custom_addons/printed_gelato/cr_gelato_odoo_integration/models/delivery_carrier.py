from odoo import _, api, fields, models
from odoo.exceptions import UserError
import requests
from odoo.exceptions import UserError
from odoo.addons.cr_gelato_odoo_integration import const
import logging

_logger = logging.getLogger(__name__)


class Carrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[('gelato', "Gelato")],
        ondelete={'gelato': 'cascade'}
    )
    cr_gelato_shipping_service_type = fields.Selection(
        string="Shipping Service Type of Gelato",
        selection=[('normal', "Standard Delivery"), ('express', "Express Delivery")],
        required=True,
        default='normal',
    )

    def _is_available_for_order(self, order):
        # _logger.info(f"product {order.order_line.product_id.name}")
        _logger.info(f"self {self}")
        _logger.info(f"delivery_type {self.delivery_type}")
        ref = super()._is_available_for_order(order)
        _logger.info(f"==========15246125===========================")
        _logger.info(f"ref {ref}")
        is_order_is_gelato_order = any(order.order_line.product_id.mapped('cr_product_uid'))
        _logger.info(f"==========================================")
        _logger.info(f"is_order_is_gelato_order {is_order_is_gelato_order}")
        _logger.info(f"==========================================")
        is_delivery_is_gelato_delivery = self.delivery_type == 'gelato'
        _logger.info(f"==========================================")
        _logger.info(f"is_delivery_is_gelato_delivery {is_delivery_is_gelato_delivery}")
        _logger.info(f"==========================================")
        # if is_order_is_gelato_order:
        #     if is_delivery_is_gelato_delivery == False:
        #         self.delivery_type = 'gelato'
        # if not is_order_is_gelato_order:
        #     if is_delivery_is_gelato_delivery == True:
        #         self.delivery_type = 'fixed'

        if is_order_is_gelato_order and not is_delivery_is_gelato_delivery or not is_order_is_gelato_order and is_delivery_is_gelato_delivery:
            _logger.info(f"==========================================")
            _logger.info(f"YYYYYYYYYYYYYYYYYYYYYYYY")
            _logger.info(f"==========================================")
            return False

        return ref

    # def available_carriers(self, partner):
    #     available_methods_for_delivery = super().available_carriers(partner)
    #     _logger.info(f"==========================================")
    #     _logger.info(f"available_methods_for_delivery {available_methods_for_delivery}")
    #     _logger.info(f"self {self}")
    #     _logger.info(f"product {self.product_id}")
    #     _logger.info(f"==========================================")
    #     return  available_methods_for_delivery.filtered(lambda x: x.delivery_type == 'gelato')
    # is_order_is_gelato_order = any(self.order_line.product_id.mapped('cr_product_uid'))
    # if is_order_is_gelato_order:
    #     return available_methods_for_delivery.filtered(lambda x: x.delivery_type == 'gelato')
    # else:
    #     return available_methods_for_delivery.filtered(lambda x: x.delivery_type != 'gelato')

    def gelato_rate_shipment(self, order):
        _logger.info(f"gelato_rate_shipment")
        if error_message := self._verify_partner_address(order.partner_id):
            return {
                'success': False,
                'price': 0,
                'error_message': error_message,
            }

        payload = {
            'orderReferenceId': order.id,
            'customerReferenceId': order.partner_id.id,
            'currency': order.currency_id.name,
            'allowMultipleQuotes': 'true',
            'products': order.items_for_order(),
            'recipient': order.partner_shipping_id.prepare_address_values(),
        }
        try:
            api_key = order.company_id.sudo().api_key_for_gelato
            order_data = self.gelato_api_request(api_key, 'order', 'v4', 'orders:quote', payload=payload)
        except UserError as e:
            return {
                'success': False,
                'price': 0,
                'error_message': str(e),
            }

        _logger.info(f"==========================================")
        _logger.info(f"order_data {order_data}")
        _logger.info(f"==========================================")
        # Find the total delivery price by summing all products' matching methods' minimum price.
        total_delivery_price = 0
        for quote_data in order_data['quotes']:
            matching_shipment_method_prices = [
                shipment_method_data['price']
                for shipment_method_data in quote_data['shipmentMethods']
                if shipment_method_data['type'] == self.cr_gelato_shipping_service_type
            ]
            if not matching_shipment_method_prices:
                return {
                    'success': False,
                    'price': 0,
                    'error_message': _("The delivery method is not available for this order."),
                }
            else:
                total_delivery_price += min(matching_shipment_method_prices)

        return {
            'success': True,
            'price': total_delivery_price,
        }

    def gelato_api_request(self, api_key, subdomain, version, endpoint, payload=None):
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        try:
            _logger.info(f"Sending post request to {endpoint}")

            url = f'https://{subdomain}.gelatoapis.com/{version}/{endpoint}'
            headers = {
                'X-API-KEY': api_key or None
            }
            response = requests.post(url=url, json=payload, headers=headers, timeout=10)
            response_content = response.json()

            _logger.info(f"Response Status: {response.status_code} and response : {response_content}")
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            _logger.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            _logger.error(f"Request error occurred: {req_err}")
        except Exception as err:
            _logger.error(f"Unexpected error occurred: {err}")

        return None

    @api.model
    def _verify_partner_address(self, partner):
        _logger.info(f"_verify_partner_address")
        required_fields_for_address = ['city', 'country_id', 'street']
        if partner.country_id.code not in const.COUNTRIES_WITHOUT_ZIPCODE:
            required_fields_for_address.append('zip')
        address_missing_fields = [
            partner._fields[field_name]
            for field_name in required_fields_for_address if not partner[field_name]
        ]
        if address_missing_fields:
            address_translated_field_names = [data._description_string(self.env) for data in address_missing_fields]
            return _(
                "The following essential address fields have not been provided: %s",
                ", ".join(address_translated_field_names),
            )

    def rate_shipment(self, order):
        self.ensure_one()
        _logger.info(f"==================44444444444========================")
        if hasattr(self, '%s_rate_shipment' % self.delivery_type):
            _logger.info(f"IF3333333333")
            res = getattr(self, '%s_rate_shipment' % self.delivery_type)(order)
            # apply fiscal position
            company = self.company_id or order.company_id or self.env.company
            if self.delivery_type == 'gelato':
                cr_price = self.gelato_rate_shipment(order)
                res['price'] = cr_price["price"]
                res['carrier_price'] = res['price']
                res['warning_message'] = False
                return res
            else:
                return super().rate_shipment(order)



