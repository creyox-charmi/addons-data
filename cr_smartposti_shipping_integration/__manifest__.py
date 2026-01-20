{
    "name": "SmartPosti Delivery Integration | SmartPosti Integration Solutions |SmartPosti Integration |SmartPosti Shipping Integration In Odoo",
    "version": "17.0.5.0.0",
    "category": "Inventory/Delivery",
    "summary": "SmartPosti (Itella/Posti) delivery carrier integration for Odoo 17",
    "description": """
SmartPosti Delivery Integration
===============================

This module provides integration with SmartPosti (Itella/Posti) delivery services:

Features:
* Create shipments and generate labels
* Track packages
* Sync pickup points/places
* Support for different destination types (APT, IPB, PO, PUDO)
* COD payment support
* Multiple additional services (Express, ID check, Age check, etc.)
* Support for EE, FI, LV, LT destinations

Supported Services:
* Parcel terminals (Blue boxes - APT, White boxes - IPB)
* Post offices (PO)
* Parcel points (PUDO) 
* Door-to-door delivery
* Express delivery
* Temperature sensitive items
    """,
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "license": "OPL-1",
    "depends": [
        "base",
        "website",
        "website_sale",
        "delivery",
        "stock",
        "sale_management",
        "sale_stock",
        "stock_delivery",
    ],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "data/delivery_carrier_data.xml",
        "views/delivery_carrier_views.xml",
        "views/smartposti_place_views.xml",
        "views/stock_picking_views.xml",
        "views/website_sale_delivery_templates.xml",
        "views/smartposti_country_price.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "cr_smartposti_shipping_integration/static/src/css/smartposti_delivery.css",
            "cr_smartposti_shipping_integration/static/src/js/smartposti_delivery.js",
        ]
    },
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
