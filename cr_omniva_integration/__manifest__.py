# -*- coding: utf-8 -*-
{
    "name": "Omniva Shipping Integration | Omniva Delivery Integration | Omniva Integration Solutions | Omniva Integration | Omniva Shipping Integration In Odoo",
    "version": "17.0.6.0.0",
    "category": "Inventory/Delivery",
    "summary": """
        The Omniva Shipping Integration module is a powerful and efficient tool for businesses using Odoo,
        enabling seamless connectivity with Omniva's shipping services. 
        It simplifies the management of shipping operations such as generating shipments, printing labels, 
        tracking parcels, and handling delivery orders directly from the Odoo interface.

        Shipping Integration,
        Omniva Shipping Integration,
        Omniva Delivery Integration,
        Omniva Integration,
        Omniva Integration Solutions,
        Shipping Integration in Odoo,
        Omniva Shipping Integration in Odoo,
        Omniva Delivery Integration in Odoo,
        Omniva Integration Solutions in Odoo,
    """,
    "description": """
        The Omniva Shipping Integration module is a powerful and efficient tool for businesses using Odoo,
        enabling seamless connectivity with Omniva's shipping services. 
        This module allows smooth management of various shipping operations — including generating shipments via Omniva API, 
        printing shipping labels, tracking deliveries, cancelling shipments, and managing delivery orders — 
        all directly within the Odoo interface.

        Key Features:
        --------------
        - Create shipments through the Omniva API.
        - Generate and download Omniva shipping labels.
        - Track real-time shipment status directly from Odoo.
        - Support for Business-to-Client (B2C) shipments.
        - Simplified delivery order handling and management.

        Keywords:
        Shipping Integration,
        Omniva Shipping Integration,
        Omniva Delivery Integration,
        Omniva Integration,
        Omniva Integration Solutions,
        Shipping Integration in Odoo,
        Omniva Shipping Integration in Odoo,
        Omniva Delivery Integration in Odoo,
        Omniva Integration Solutions in Odoo,
    """,
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "depends": [
        "base",
        "delivery",
        "stock",
        "sale_management",
        "sale_stock",
        "stock_delivery",
        "website",
        "website_sale",
    ],
    "assets": {
        "web.assets_frontend": [
            "cr_omniva_integration/static/src/js/omniva_delivery.js"
        ]
    },
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "data/delivery_carrier_data.xml",
        "views/delivery_carrier_views.xml",
        "views/omniva_location_views.xml",
        "views/website_sale_delivery_templates.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
