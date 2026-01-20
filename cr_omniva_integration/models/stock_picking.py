# -*- coding: utf-8 -*-

import requests
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    omniva_barcode = fields.Char(string="Omniva Barcode", copy=False, readonly=True)
    omniva_partner_shipment_id = fields.Char(string="Partner Shipment ID", copy=False)
    omniva_label_id = fields.Many2one(
        "ir.attachment", string="Omniva Label", copy=False, readonly=True, store=True
    )

    def button_validate(self):
        """Override to send shipment to Omniva when validating."""
        res = super().button_validate()

        for picking in self:
            if (
                picking.carrier_id
                and picking.carrier_id.delivery_type == "omniva"
                and not picking.omniva_barcode
                and picking.picking_type_code == "outgoing"
            ):

                try:
                    picking.omniva_send_shipping()
                except Exception as e:
                    picking.message_post(
                        body=_(
                            "Warning: Failed to create Omniva shipment automatically: %s"
                        )
                        % str(e),
                        message_type="comment",
                    )
        return res

    def action_omniva_send_shipping(self):
        """Manual action to send shipment to Omniva."""
        self.ensure_one()

        if not self.carrier_id or self.carrier_id.delivery_type != "omniva":
            raise UserError(_("This is not an Omniva shipment."))

        if self.omniva_barcode:
            raise UserError(
                _("Shipment already sent to Omniva. Barcode: %s") % self.omniva_barcode
            )

        try:
            self.omniva_send_shipping()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Omniva shipment created successfully! Barcode: %s")
                    % self.omniva_barcode,
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            raise UserError(_("Failed to create Omniva shipment: %s") % str(e))

    def _validate_and_format_phone(self, phone_number):
        """Validate and format phone number for Omniva API."""
        if not phone_number:
            return None

        clean = "".join(c for c in str(phone_number) if c.isdigit() or c == "+")
        digit_count = len(clean.replace("+", ""))

        if digit_count < 8:
            return None

        if not clean.startswith("+"):
            if digit_count >= 10:
                clean = "+" + clean
            else:
                return None

        if len(clean) > 12:
            clean = clean[:12]

        if len(clean.replace("+", "")) < 8:
            return None

        return clean

    def _prepare_omniva_headers(self):
        """Prepare authentication headers for Omniva API."""
        company = self.company_id

        if not company.omniva_username or not company.omniva_password:
            raise ValidationError(
                _("Omniva credentials not configured in company settings.")
            )

        credentials = f"{company.omniva_username}:{company.omniva_password}"
        auth_token = base64.b64encode(credentials.encode("utf-8")).decode("ascii")

        return {
            "Authorization": f"Basic {auth_token}",
            "X-Integration-Agent-Id": company.omniva_developer_id
            or "Developer_ODOO18_v1",
            "Content-Type": "application/json",
        }

    def _get_omniva_country_code(self, country_code):
        """Convert country code to Omniva-compatible code."""
        if not country_code:
            return "EE"

        omniva_sender_countries = ["EE", "LV", "LT"]

        if country_code in omniva_sender_countries:
            return country_code

        return "EE"

    def _prepare_omniva_shipment_data(self):
        """Prepare shipment data for Omniva API."""
        self.ensure_one()
        company = self.company_id
        carrier = self.carrier_id
        partner = self.partner_id

        if not company.omniva_customer_code:
            raise ValidationError(
                _("Customer Code not configured in company settings.")
            )

        required_partner_fields = {
            "Name": partner.name,
            "Street": partner.street,
            "City": partner.city,
            "Zip": partner.zip,
            "Country": partner.country_id.code if partner.country_id else None,
        }

        missing_fields = [
            field for field, value in required_partner_fields.items() if not value
        ]
        if missing_fields:
            raise ValidationError(
                _("Missing required delivery partner fields: %s")
                % ", ".join(missing_fields)
            )

        # Get delivery channel from sale order
        delivery_channel = carrier.omniva_delivery_channel or "COURIER"

        if self.sale_id and self.sale_id.omniva_delivery_channel:
            delivery_channel = self.sale_id.omniva_delivery_channel
            carrier.omniva_delivery_channel = delivery_channel

        # Validate contact information based on delivery channel
        if delivery_channel == "COURIER":
            if not partner.phone and not partner.mobile:
                raise ValidationError(
                    _(
                        "Courier delivery requires at least phone or mobile number for the delivery partner."
                    )
                )
        elif delivery_channel in ["POST_OFFICE", "PARCEL_MACHINE"]:
            if not partner.mobile and not partner.email:
                raise ValidationError(
                    _(
                        "%s delivery requires at least mobile number or email for the delivery partner."
                    )
                    % delivery_channel.replace("_", " ").title()
                )

        # Prepare receiver addressee
        receiver_address = {
            "personName": partner.name[:50],
            "address": {
                "street": partner.street[:80],
                "deliverypoint": partner.city[:80],
                "postcode": partner.zip[:10],
                "country": partner.country_id.code,
            },
        }

        if partner.street2:
            receiver_address["address"]["apartmentNo"] = partner.street2[:20]

        # ========== CRITICAL FIX: Validate location type matches delivery channel ==========
        if self.sale_id and self.sale_id.omniva_location_id:
            location = self.sale_id.omniva_location_id

            # Validate location type matches delivery channel
            if delivery_channel == "PARCEL_MACHINE":
                # For parcel machine, location MUST be type '0' (Parcel Machine)
                if location.location_type != "0":
                    raise ValidationError(
                        _(
                            'Selected location "%s" is not a Parcel Machine.\n'
                            "Please select a Parcel Machine location for PARCEL_MACHINE delivery channel.\n\n"
                            "Location Type: %s"
                        )
                        % (
                            location.name,
                            dict(location._fields["location_type"].selection).get(
                                location.location_type
                            ),
                        )
                    )
                # Add offloadPostcode (mandatory for parcel machines)
                if location.zip_code:
                    receiver_address["address"]["offloadPostcode"] = location.zip_code[
                        :10
                    ]
                else:
                    raise ValidationError(
                        _(
                            'Selected Parcel Machine "%s" does not have a valid postcode.'
                        )
                        % location.name
                    )

            elif delivery_channel == "POST_OFFICE":
                # For post office, location MUST be type '1' (Post Office)
                if location.location_type != "1":
                    raise ValidationError(
                        _(
                            'Selected location "%s" is not a Post Office.\n'
                            "Please select a Post Office location for POST_OFFICE delivery channel.\n\n"
                            "Location Type: %s"
                        )
                        % (
                            location.name,
                            dict(location._fields["location_type"].selection).get(
                                location.location_type
                            ),
                        )
                    )
                # Add offloadPostcode (optional for post offices, but recommended)
                if location.zip_code:
                    receiver_address["address"]["offloadPostcode"] = location.zip_code[
                        :10
                    ]

            # For COURIER: do NOT add offloadPostcode at all (per API docs)
            # No need for else block - we simply don't add offloadPostcode for courier

        # Add contact info with validation
        validated_phone = self._validate_and_format_phone(partner.phone)
        validated_mobile = self._validate_and_format_phone(partner.mobile)

        destination_country = partner.country_id.code if partner.country_id else "EE"
        is_international = destination_country not in ["EE", "LV", "LT", "FI"]

        if validated_phone:
            receiver_address["contactPhone"] = validated_phone
            if is_international and not validated_mobile:
                receiver_address["contactMobile"] = validated_phone

        if validated_mobile:
            receiver_address["contactMobile"] = validated_mobile
        if partner.email:
            receiver_address["contactEmail"] = partner.email[:50]

        # Re-validate contact methods after cleaning
        if delivery_channel == "COURIER":
            if not validated_phone and not validated_mobile:
                raise ValidationError(
                    _(
                        "Courier delivery requires a valid phone or mobile number.\n"
                        "Phone: %s\nMobile: %s\n"
                        "Please ensure phone numbers are in international format (e.g., +372XXXXXXXX)"
                    )
                    % (
                        partner.phone or "Not provided",
                        partner.mobile or "Not provided",
                    )
                )
        elif delivery_channel in ["POST_OFFICE", "PARCEL_MACHINE"]:
            if not validated_mobile and not partner.email:
                raise ValidationError(
                    _(
                        "%s delivery requires a valid mobile number or email.\n"
                        "Mobile: %s\nEmail: %s\n"
                        "Please ensure mobile number is in international format (e.g., +372XXXXXXXX)"
                    )
                    % (
                        delivery_channel.replace("_", " ").title(),
                        partner.mobile or "Not provided",
                        partner.email or "Not provided",
                    )
                )

        # Prepare sender addressee
        sender_address = {
            "personName": company.name[:50],
            "address": {
                "street": (company.street or "Main Street")[:80],
                "deliverypoint": (company.city or "City")[:80],
                "postcode": (company.zip or "10111")[:10],
                "country": self._get_omniva_country_code(
                    company.country_id.code if company.country_id else None
                ),
            },
        }

        validated_sender_phone = self._validate_and_format_phone(company.phone)
        if validated_sender_phone:
            sender_address["contactPhone"] = validated_sender_phone
        if company.email:
            sender_address["contactEmail"] = company.email[:50]

        if not self.omniva_partner_shipment_id:
            self.omniva_partner_shipment_id = f"ODO_{self.name.replace('/', '_')}"

        # Prepare shipment payload
        shipment_data = {
            "mainService": carrier.omniva_main_service or "PARCEL",
            "deliveryChannel": delivery_channel,
            "partnerShipmentId": self.omniva_partner_shipment_id,
            "receiverAddressee": receiver_address,
            "senderAddressee": sender_address,
        }

        # Add service package for international PARCEL
        if carrier.omniva_main_service == "PARCEL" and is_international:
            shipment_data["servicePackage"] = {"code": "ECONOMY"}
        elif carrier.omniva_service_package:
            if carrier.omniva_main_service == "LETTER" or is_international:
                shipment_data["servicePackage"] = {
                    "code": carrier.omniva_service_package
                }

        # Add content description for international shipments
        content_desc = self.origin or "Goods"
        if partner.country_id and partner.country_id.code not in [
            "EE",
            "LV",
            "LT",
            "FI",
        ]:
            if self.sale_id and self.sale_id.note:
                content_desc = self.sale_id.note[:500]
            shipment_data["contentDescription"] = content_desc

        # Add weight if available
        if self.shipping_weight and self.shipping_weight > 0:
            shipment_data["measurement"] = {"weight": round(self.shipping_weight, 3)}

        # Add shipment comment
        if self.note:
            shipment_data["shipmentComment"] = self.note[:128]

        # Add customs data for non-EU destinations
        eu_countries = [
            "AT",
            "BE",
            "BG",
            "HR",
            "CY",
            "CZ",
            "DK",
            "EE",
            "FI",
            "FR",
            "DE",
            "GR",
            "HU",
            "IE",
            "IT",
            "LV",
            "LT",
            "LU",
            "MT",
            "NL",
            "PL",
            "PT",
            "RO",
            "SK",
            "SI",
            "ES",
            "SE",
        ]

        if is_international and destination_country not in eu_countries:
            if not company.omniva_default_hs_code:
                raise ValidationError(
                    _(
                        "Default HS Code not configured for Omniva shipments.\n\n"
                        'Go to Settings > Companies > [Your Company] and set "Default Omniva HS Code".'
                    )
                )

            if not self.move_ids:
                raise ValidationError(
                    _("No stock moves found for customs declaration.")
                )

            first_move = self.move_ids[0]
            item_description = (first_move.product_id.name or content_desc)[:500]

            total_value = self.sale_id.amount_untaxed if self.sale_id else 10.0
            total_pieces = int(sum(self.move_ids.mapped("product_uom_qty")) or 1)
            total_weight = self.shipping_weight or float(total_pieces)

            per_piece_weight = round(total_weight / total_pieces, 3)
            per_piece_value = round(total_value / total_pieces, 2)

            shipment_data["customs"] = {
                "goodsCategoryCode": "SALE_OF_GOODS",
                "shipmentItems": [
                    {
                        "description": item_description,
                        "numberOfPieces": total_pieces,
                        "weight": per_piece_weight,
                        "financialValue": per_piece_value,
                        "tariffNumber": company.omniva_default_hs_code,
                        "originCountry": self._get_omniva_country_code(
                            company.country_id.code if company.country_id else None
                        ),
                    }
                ],
            }

        return {
            "customerCode": company.omniva_customer_code,
            "fileId": f"FILE_{fields.Datetime.now().strftime('%Y%m%d%H%M%S')}_{self.id}",
            "shipments": [shipment_data],
        }

    def omniva_send_shipping(self):
        """Send shipment to Omniva API."""
        self.ensure_one()
        company = self.company_id
        base_url = company._get_omniva_base_url()

        headers = self._prepare_omniva_headers()
        payload = self._prepare_omniva_shipment_data()

        import json
        import logging

        _logger = logging.getLogger(__name__)

        try:
            response = requests.post(
                f"{base_url}/shipments/business-to-client",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code in [200, 201]:
                result = response.json()

                if result.get("resultCode") == "OK" and result.get("savedShipments"):
                    saved_shipment = result["savedShipments"][0]
                    self.omniva_barcode = saved_shipment.get("barcode")
                    self.carrier_tracking_ref = self.omniva_barcode

                    self.message_post(
                        body=_("Omniva shipment created successfully.<br/>Barcode: %s")
                        % self.omniva_barcode
                    )

                    try:
                        self._omniva_get_label()
                    except Exception as label_error:
                        self.message_post(
                            body=_(
                                "Shipment created but label generation failed: %s<br/>"
                                "You can try to generate the label manually later."
                            )
                            % str(label_error),
                            message_type="comment",
                        )

                elif result.get("failedShipments"):
                    failed = result["failedShipments"][0]
                    error_msg = failed.get("message", "Unknown error")
                    error_code = failed.get("messageCode", "")

                    raise ValidationError(
                        _(
                            "Omniva shipment creation failed:\n\n"
                            "Error Code: %s\n"
                            "Message: %s\n\n"
                            "Please check the delivery address and contact information."
                        )
                        % (error_code, error_msg)
                    )
                else:
                    raise ValidationError(
                        _(
                            "Unexpected response from Omniva API. No shipments saved or failed."
                        )
                    )

            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get(
                        "message", error_data.get("error", response.text)
                    )
                except:
                    error_msg = response.text

                raise ValidationError(
                    _("Omniva API error (Status %s):\n%s")
                    % (response.status_code, error_msg)
                )

        except requests.RequestException as e:
            raise ValidationError(
                _(
                    "Network error while connecting to Omniva:\n%s\n\n"
                    "Please check your internet connection."
                )
                % str(e)
            )

    def _omniva_get_label(self):
        """Request shipping label from Omniva."""
        self.ensure_one()

        if not self.omniva_barcode:
            raise ValidationError(_("No barcode available. Create shipment first."))

        company = self.company_id
        base_url = company._get_omniva_base_url()
        headers = self._prepare_omniva_headers()

        payload = {
            "customerCode": company.omniva_customer_code,
            "barcodes": [{"barcode": self.omniva_barcode}],
            "sendAddressCardTo": "RESPONSE",
        }

        import json
        import logging

        _logger = logging.getLogger(__name__)

        try:
            response = requests.post(
                f"{base_url}/shipments/package-labels",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()

                if result.get("successAddressCards"):
                    label_info = result["successAddressCards"][0]
                    label_data = label_info.get("fileData")

                    if label_data:
                        if self.omniva_label_id:
                            self.omniva_label_id.unlink()

                        attachment = self.env["ir.attachment"].create(
                            {
                                "name": f'Omniva_Label_{self.name.replace("/", "_")}.pdf',
                                "type": "binary",
                                "datas": label_data,
                                "res_model": self._name,
                                "res_id": self.id,
                                "mimetype": "application/pdf",
                            }
                        )

                        self.omniva_label_id = attachment.id

                        self.message_post(
                            body=_("Omniva shipping label generated successfully."),
                            attachment_ids=[attachment.id],
                        )
                    else:
                        raise ValidationError(_("No label data in response"))

                elif result.get("failedAddressCards"):
                    failed = result["failedAddressCards"][0]
                    error_msg = failed.get("message", "Unknown error")
                    raise ValidationError(_("Label generation failed: %s") % error_msg)
                else:
                    raise ValidationError(_("Unexpected label response"))

            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get(
                        "message", error_data.get("error", response.text)
                    )
                except:
                    error_msg = response.text

                raise ValidationError(
                    _("Label request failed (Status %s): %s")
                    % (response.status_code, error_msg)
                )

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(_("Error generating label: %s") % str(e))

    def action_omniva_get_label(self):
        """Manual action to regenerate label."""
        self.ensure_one()

        if not self.omniva_barcode:
            raise UserError(
                _("No Omniva barcode found. Please create the shipment first.")
            )

        try:
            self._omniva_get_label()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Label generated successfully!"),
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            raise UserError(_("Failed to generate label: %s") % str(e))

    def omniva_tracking_url(self):
        """Generate tracking URL for Omniva shipment."""
        self.ensure_one()

        if not self.omniva_barcode:
            return False

        return f"https://www.omniva.ee/track?barcode={self.omniva_barcode}"

    def action_open_omniva_tracking(self):
        """Open Omniva tracking page."""
        self.ensure_one()
        url = self.omniva_tracking_url()

        if not url:
            raise UserError(
                _(
                    "No tracking information available. Please create the shipment first."
                )
            )

        return {"type": "ir.actions.act_url", "url": url, "target": "new"}

    def action_omniva_cancel_shipment(self):
        """Cancel Omniva shipment (if in REGISTERED status)."""
        self.ensure_one()

        if not self.omniva_barcode:
            raise UserError(_("No Omniva shipment to cancel."))

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Information"),
                "message": _(
                    "Shipment cancellation must be done through Omniva portal or contact support.\n"
                    "Barcode: %s"
                )
                % self.omniva_barcode,
                "type": "info",
                "sticky": True,
            },
        }
