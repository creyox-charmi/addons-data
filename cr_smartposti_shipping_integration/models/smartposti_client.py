# -*- coding: utf-8 -*-
"""SmartPosti API Client"""

import json
import logging

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SmartPostiClient:
    """Client for SmartPosti API communication"""

    def __init__(self, base_url, api_key=None, gateway_secret=None, timeout=30):
        """Initialize API client

        Args:
            base_url: SmartPosti API base URL
            api_key: API authentication key (optional)
            gateway_secret: Gateway secret (optional)
            timeout: Request timeout in seconds
        """
        if not base_url:
            raise UserError("SmartPosti API URL not configured")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Setup headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if api_key:
            self.headers["Authorization"] = api_key
        if gateway_secret:
            self.headers["X-GATEWAY-SECRET"] = gateway_secret

    def _build_url(self, endpoint):
        """Build complete API URL

        Args:
            endpoint: API endpoint path

        Returns:
            str: Complete URL
        """
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _handle_error(self, error, operation):
        """Handle and log API errors

        Args:
            error: Exception object
            operation: Operation description

        Raises:
            UserError: With formatted error message
        """
        error_msg = f"SmartPosti API {operation} failed: {str(error)}"
        _logger.error(error_msg)

        if isinstance(error, Timeout):
            raise UserError(f"API timeout during {operation}. Please try again.")
        elif isinstance(error, ConnectionError):
            raise UserError(
                f"Cannot connect to SmartPosti API. Check network connection."
            )
        else:
            raise UserError(error_msg)

    def _extract_error_details(self, response):
        """Extract error details from API response

        Args:
            response: requests.Response object

        Returns:
            str: Error details or empty string
        """
        try:
            error_json = response.json()
            if "error" in error_json:
                return f"\nAPI Error: {error_json['error']}"
            elif "errors" in error_json:
                return f"\nAPI Errors: {error_json['errors']}"
        except:
            try:
                error_text = response.text
                if error_text:
                    return f"\nResponse: {error_text[:500]}"
            except:
                pass
        return ""

    def _make_request(self, method, endpoint, params=None, json_data=None):
        """Make HTTP request to API

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            params: Query parameters (optional)
            json_data: JSON payload (optional)

        Returns:
            dict or bytes: Response data

        Raises:
            UserError: On request failure
        """
        url = self._build_url(endpoint)

        try:
            if method.upper() == "GET":
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=self.timeout
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url, headers=self.headers, json=json_data, timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Handle response based on content type
            content_type = response.headers.get("Content-Type", "").lower()

            if "application/json" in content_type:
                return response.json()
            elif "application/pdf" in content_type:
                return {
                    "binary": response.content,
                    "content_type": content_type,
                    "filename": f"label_{len(response.content)}.pdf",
                }
            else:
                return {"binary": response.content, "content_type": content_type}

        except RequestException as e:
            error_detail = str(e)

            if hasattr(e, "response") and e.response is not None:
                error_detail += self._extract_error_details(e.response)

            self._handle_error(Exception(error_detail), f"{method} {endpoint}")

        except json.JSONDecodeError as e:
            _logger.error(f"Invalid JSON response: {str(e)}")
            raise UserError("Invalid JSON response from SmartPosti API")

    def get_places(self, country, place_type=None, filter_type=None):
        """Fetch pickup places/locations

        Args:
            country: Country code (EE, FI, LV, LT)
            place_type: Place type filter (optional)
            filter_type: Additional filter (optional)

        Returns:
            dict: Places data from API
        """
        params = {"country": country}
        if place_type:
            params["type"] = place_type
        if filter_type:
            params["filter"] = filter_type

        return self._make_request("GET", "places", params=params)

    def create_order(self, order_data):
        """Create shipment order

        Args:
            order_data: Order payload dict

        Returns:
            dict: Order creation response
        """
        if not order_data:
            raise UserError("Order data is required")

        return self._make_request("POST", "orders", json_data=order_data)

    def get_labels(self, barcodes, format_type="A5"):
        """Fetch shipping labels

        Args:
            barcodes: Barcode or list of barcodes
            format_type: Label format (A4/4, A5, etc.)

        Returns:
            dict: Label data (binary PDF)
        """
        if isinstance(barcodes, str):
            barcodes = [barcodes]

        params = {
            "format": format_type,
            "barcode": barcodes[0] if len(barcodes) == 1 else barcodes,
        }

        return self._make_request("GET", "labels", params=params)

    def track_shipment(self, barcode=None, reference=None):
        """Track shipment status

        Args:
            barcode: Tracking barcode (optional)
            reference: Order reference (optional)

        Returns:
            dict: Tracking information
        """
        if not barcode and not reference:
            raise UserError("Either barcode or reference is required")

        params = {}
        if barcode:
            params["barcode"] = barcode
        if reference:
            params["reference"] = reference

        return self._make_request("GET", "tracking", params=params)
