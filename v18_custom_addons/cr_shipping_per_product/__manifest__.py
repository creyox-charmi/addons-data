# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Shipping Per Product | Product-Specific Delivery | Product-Specific Delivery | Individual Product Shipping",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0",
    "summary":
        """
        The Shipping Per Product module addresses the need for flexibility in shipping methods by allowing businesses to
        assign specific delivery carriers to each product in their inventory. When configuring a sale order or quotation, 
        the user can easily select the delivery method per product, ensuring that shipping costs are calculated correctly 
        and included in the final invoice.This module is particularly useful for businesses that sell multiple products 
        with varying shipping needs and costs, offering flexibility and control over their shipping methods and fees.
        
        Shipping Per Product
        Shipping Per Product in odoo
        Product-Specific Delivery
        Product-Specific Delivery in odoo
        Individual Product Shipping
        Individual Product Shipping in odoo
        Shipping Allocation per Product
        Shipping Allocation per Product in odoo
        Shipping Cost per Item
        Shipping Cost per Item in odoo
        Per-Product Shipping Configuration
        Per-Product Shipping Configuration in odoo
        Custom Shipping per Item
        Custom Shipping per Item in odoo
        Shipping Options for Products
        Shipping Options for Products in odoo
        Custom Delivery per Product
        Custom Delivery per Product in odoo
        
        "How to assign different delivery carriers to each product?"
        "Shipping by product instead of order"
        "How to calculate shipping per product in my e-commerce store?"
        "Customizable delivery methods per product"
        "Shipping cost calculation per product in invoice"
        "Shipping cost per product for sales orders"
        "How to include product-specific shipping fees in invoice?"
        "Shipping charges per product in quotation"
        "Track shipping costs and methods by product"
        "How to set up shipping fees by product in my store?"
        "Shipping per product module for Odoo"
        "Integrate custom shipping methods for each product"
        "Shipping per product feature in Odoo"
        "Best shipping modules for Odoo"
        "Odoo shipping management by product"
        "How to configure delivery methods by product in Odoo?"
        "Shipping flexibility for multi-product businesses"
        "Shipping solutions for businesses with diverse products"
        "Set delivery methods for specific products in inventory"
        "How does shipping per product feature work?"
        "How to improve shipping efficiency with product-specific delivery methods"
        """,
    "sequence": 10,
    "description":
        """
        The Shipping Per Product module addresses the need for flexibility in shipping methods by allowing businesses to
        assign specific delivery carriers to each product in their inventory. When configuring a sale order or quotation, 
        the user can easily select the delivery method per product, ensuring that shipping costs are calculated correctly 
        and included in the final invoice.This module is particularly useful for businesses that sell multiple products 
        with varying shipping needs and costs, offering flexibility and control over their shipping methods and fees.
        
        Shipping Per Product
        Shipping Per Product in odoo
        Product-Specific Delivery
        Product-Specific Delivery in odoo
        Individual Product Shipping
        Individual Product Shipping in odoo
        Shipping Allocation per Product
        Shipping Allocation per Product in odoo
        Shipping Cost per Item
        Shipping Cost per Item in odoo
        Per-Product Shipping Configuration
        Per-Product Shipping Configuration in odoo
        Custom Shipping per Item
        Custom Shipping per Item in odoo
        Shipping Options for Products
        Shipping Options for Products in odoo
        Custom Delivery per Product
        Custom Delivery per Product in odoo
        
        "How to assign different delivery carriers to each product?"
        "Shipping by product instead of order"
        "How to calculate shipping per product in my e-commerce store?"
        "Customizable delivery methods per product"
        "Shipping cost calculation per product in invoice"
        "Shipping cost per product for sales orders"
        "How to include product-specific shipping fees in invoice?"
        "Shipping charges per product in quotation"
        "Track shipping costs and methods by product"
        "How to set up shipping fees by product in my store?"
        "Shipping per product module for Odoo"
        "Integrate custom shipping methods for each product"
        "Shipping per product feature in Odoo"
        "Best shipping modules for Odoo"
        "Odoo shipping management by product"
        "How to configure delivery methods by product in Odoo?"
        "Shipping flexibility for multi-product businesses"
        "Shipping solutions for businesses with diverse products"
        "Set delivery methods for specific products in inventory"
        "How does shipping per product feature work?"
        "How to improve shipping efficiency with product-specific delivery methods"
        """,
    "category": "Warehouse",
    "price": "29",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "stock", "sale", "stock_delivery"],
    "data": [
        "security/ir.model.access.csv",
        "views/per_product_shipping.xml",
        "views/delivery_carrier.xml",
        "views/product_template.xml",
        "wizard/choose_delivery_carrier_view.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
