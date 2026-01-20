import logging
import pprint

from werkzeug.exceptions import Forbidden

from odoo import _
from odoo.http import Controller, request, route

_logger = logging.getLogger(__name__)


class GelatoWebhookkController(Controller):
    _webhook_url = '/gelato/webhook'

    @route(_webhook_url, type='http', methods=['POST'], auth='public', csrf=False)
    def webhook_details_from_gelato(self):
        data_info = request.get_json_data()
        # _logger.info("Webhook notification received from Gelato:\n%s", pprint.pformat(data_info))
        x = data_info['event']
        _logger.info(f"event : {data_info}")
        # if data_info['event'] == 'store_product_created':
        #     product = request.env['product.template'].sudo().create({
        #                     'name': data_info['title'],
        #                 })
        #     _logger.info(f"TEMPLATE CREATE.. product {product}")
        #     if product:
        #         product.create_store_product(data_info)

        if data_info['event'] == 'order_status_updated':
            sale_order_id = int(data_info['orderReferenceId'])
            is_sale_order_id_exist = request.env['sale.order'].sudo().browse(sale_order_id).exists()
            if is_sale_order_id_exist:
                sale = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
                received_signature = request.httprequest.headers.get('signature', '')
                is_correct = self.is_notification_from_Correct_webhook(sale, received_signature)
                if is_correct:
                    self.order_status_event(sale, data_info)

        if data_info['event'] == 'order_item_status_updated':
            sale_order_id = int(data_info['orderReferenceId'])
            is_sale_order_id_exist = request.env['sale.order'].sudo().browse(sale_order_id).exists()
            if is_sale_order_id_exist:
                sale = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
                received_signature = request.httprequest.headers.get('signature', '')
                is_correct = self.is_notification_from_Correct_webhook(sale, received_signature)
                if is_correct:
                    self.order_status_event(sale, data_info)

        if data_info['event'] == 'store_product_template_updated':
            _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            _logger.info("ENTERRR")
            _logger.info("222222222222222222222")

            # z = request.env['ir.config_parameter'].sudo().get_param('webhook_secret_for_gelato')
            # _logger.info(f"z : {z}")
            storeProductTemplateId = data_info['storeProductTemplateId']
            _logger.info(f"storeProductTemplateId {storeProductTemplateId}")
            is_storeProductTemplateId_exist = request.env['product.template'].sudo().search(
                [('cr_template_ref', '=', storeProductTemplateId)]).exists()
            product = request.env['product.template'].sudo().search([('cr_template_ref', '=', storeProductTemplateId)])
            received_signature = request.httprequest.headers.get('signature', '')
            auth = product.is_temp_available(received_signature)
            _logger.info(f"auth {auth}")
            # received_signature = request.httprequest.headers.get('signature', '')
            # is_correct = self.is_notification_from_Correct_webhook(product,received_signature)
            # if is_correct:
            if auth:
                product.msg_notification_from_gelato(data_info['event'])

        if data_info['event'] == 'store_product_template_deleted':
            _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            _logger.info("TEMPLATE DELETE..")
            _logger.info("33333")

            storeProductTemplateId = data_info['storeProductTemplateId']
            _logger.info(f"storeProductTemplateId {storeProductTemplateId}")
            is_storeProductTemplateId_exist = request.env['product.template'].sudo().search(
                [('cr_template_ref', '=', storeProductTemplateId)]).exists()
            product = request.env['product.template'].sudo().search([('cr_template_ref', '=', storeProductTemplateId)])
            received_signature = request.httprequest.headers.get('signature', '')
            auth = product.is_temp_available(received_signature)
            _logger.info(f"auth {auth}")
            # received_signature = request.httprequest.headers.get('signature', '')
            # is_correct = self.is_notification_from_Correct_webhook(product,received_signature)
            # if is_correct:
            if auth:
                product.msg_notification_from_gelato(data_info['event'])
                cr_sale = request.env['sale.order.line'].sudo().search([('product_template_id', '=', product.id)])
                for data in cr_sale:
                    _logger.info(f"data {data}")
                    _logger.info(f"data.order_id {data.order_id}")
                    _logger.info(f"data.order_id.state1 {data.order_id.state}")
                    data.order_id.with_user(2)._action_cancel()
                    data.order_id.with_user(2).unlink()

                product.with_user(2).unlink()

        if data_info['event'] == 'store_product_template_created':
            _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            _logger.info("TEMPLATE CREATE..")
            _logger.info("1212121221")
            _logger.info(f"1212121221 {data_info['previewUrl']}")
            pro_id = data_info['storeProductTemplateId']
            product = request.env['product.template'].sudo().create({
                'name': data_info['title'],
                'cr_template_ref': data_info['storeProductTemplateId'],
            })
            _logger.info(f"TEMPLATE CREATE.. product {product}")
            if product:
                product.action_sync_gelato_template_info()
                product.set_img()

        return request.make_json_response('')

    @staticmethod
    def _extract_tracking_data(item_data):
        """ Extract the tracking URL and code from the item data.

        :param dict item_data: The item data.
        :return: The extracted tracking data.
        :rtype: dict
        """
        tracking_data = {}
        for i in item_data:
            for fulfilment_data in i['fulfillments']:
                tracking_data.setdefault(
                    fulfilment_data['trackingUrl'], fulfilment_data['trackingCode']
                )  # Different items can have the same tracking URL.
        return tracking_data

    def order_status_event(self, sale, data_info):
        if sale:
            status = data_info.get('fulfillmentStatus')
            if status == "created":
                sale.msg_notification_from_gelato(status)
            elif status == "uploading":
                sale.msg_notification_from_gelato(status)
            elif status == "passed":
                sale.msg_notification_from_gelato(status)
            elif status == "in_production":
                sale.msg_notification_from_gelato(status)
            elif status == "printed":
                sale.msg_notification_from_gelato(status)
            elif status == "draft":
                sale.msg_notification_from_gelato(status)
            elif status == "failed":
                sale.msg_notification_from_gelato(status)
            elif status == "canceled":
                sale.msg_notification_from_gelato(status)
                if sale.state != 'cancel':
                    sale.with_user(2)._action_cancel()
            elif status == "pending_approval":
                sale.msg_notification_from_gelato(status)
            elif status == "pending_personalization":
                sale.msg_notification_from_gelato(status)
            elif status == "digitizing":
                sale.msg_notification_from_gelato(status)
            elif status == "not_connected":
                sale.msg_notification_from_gelato(status)
            elif status == "on_hold":
                sale.msg_notification_from_gelato(status)
            elif status == "shipped":
                sale.msg_notification_from_gelato(status)
            elif status == "in_transit":
                sale.msg_notification_from_gelato(status)
            elif status == "delivered":
                sale.msg_notification_from_gelato(status)
            elif status == "returned":
                sale.msg_notification_from_gelato(status)
            else:
                sale.msg_notification_from_gelato(status)

    # @staticmethod
    # def is_sale_order_exist(data_info):
    #     sale_order_id = int(data_info['orderReferenceId'])
    #     is_sale_order_id_exist = request.env['sale.order'].sudo().browse(sale_order_id).exists()
    #     if is_sale_order_id_exist:
    #         return sale_order_id
    #     else:
    #         return is_sale_order_id_exist

    @staticmethod
    def is_notification_from_Correct_webhook(sale_id, received_signature):
        _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        _logger.info("]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]")
        _logger.info(f"sale_id {sale_id}")
        _logger.info(f"company_id {sale_id.company_id}")
        _logger.info(f"webhook_secret_for_gelato {sale_id.company_id.sudo().webhook_secret_for_gelato}")
        _logger.info(f"received_signature {received_signature}")
        if sale_id.company_id.sudo().webhook_secret_for_gelato != received_signature:
            _logger.warning("Received notification with invalid signature.")
        else:
            return True

