# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Sale Qutotation & Purchase RFQ Creation From Portal | Portal Order Management | Portal Sales & Purchase Creator | Portal SO/PO Creation",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Website",
    "description": """Sale Order & Purchase Order Creation From Portal is an Odoo module that enables both 
        customers and vendors to create and manage Sale Orders and Purchase Orders directly from the portal. 
        With this module, authenticated portal users gain self-service capabilities to initiate orders without 
        requiring internal users to intervene. Customers can submit sale orders for products or services, while 
        vendors can place purchase orders seamlessly from their portal accounts.

        The module ensures smooth and secure order processing by integrating with Odoo’s native sales and purchasing workflows. 
        Users can view order status, download order documents, and track order progress in real time. This reduces administrative 
        effort, speeds up the order cycle, and enhances user satisfaction through greater autonomy.
        Sale Order & Purchase Order Creation From Portal,
        Sale Qutotation & Purchase RFQ Creation From Portal,
        Portal Order Management,
        Portal Sales & Purchase Creator,
        Portal SO/PO Creation.
        What is the purpose of the Sale Qutotation & Purchase RFQ Creation From Portal?
        Can I create new customer if not a customer or vendor?
        Is there any limitation of sale quotation or purchase rfq creation per user or customer?
        How to create sale quotation & purchase rfq from portal?
        Can i create new customer or vendor for sale quotation or purchase rfq?
        """,
    "license": "OPL-1",
    "version": "17.0.0.2",
    "summary": """
        Sale Order & Purchase Order Creation From Portal is an Odoo module that enables both 
        customers and vendors to create and manage Sale Orders and Purchase Orders directly from the portal. 
        With this module, authenticated portal users gain self-service capabilities to initiate orders without 
        requiring internal users to intervene. Customers can submit sale orders for products or services, while 
        vendors can place purchase orders seamlessly from their portal accounts.

        The module ensures smooth and secure order processing by integrating with Odoo’s native sales and purchasing workflows. 
        Users can view order status, download order documents, and track order progress in real time. This reduces administrative 
        effort, speeds up the order cycle, and enhances user satisfaction through greater autonomy.
        Sale Order & Purchase Order Creation From Portal,
        Sale Qutotation & Purchase RFQ Creation From Portal,
        Portal Order Management,
        Portal Sales & Purchase Creator,
        Portal SO/PO Creation.   
        What is the purpose of the Sale Qutotation & Purchase RFQ Creation From Portal?
        Can I create new customer if i'm already not a customer or vendor?
        Is there any limitation of sale quotation or purchase rfq creation per user or customer?
        How to create sale quotation & purchase rfq from portal?
        Can i create new customer or vendor for sale quotation or purchase rfq?
    """,
    "depends": ["base", "sale_management", "purchase", "website"],
    "data": [
        "views/sale_quatation_creation_portal.xml",
        "views/purchase_rfq_creation_portal.xml",
        "views/sale_order_generated_success.xml",
        "views/purchase_order_generated_success.xml",
    ],
'assets': {
    'web.assets_frontend': [
        'cr_portal_quote_and_rfq/static/src/js/purchase_rfq.js',
    ],
},
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": [
        "static/description/banner.png",
    ],
    "price": 70,
    "currency": "USD",
}
