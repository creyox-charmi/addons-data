# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Shop Quantity | Product Pricing Tiers | Pricelist Adjustment by Quantity | Quantity-Based Discounts | Shop Quantity Limits and Price Tiers',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0",
    'summary':
        """
        This module adds a more advanced layer of control over product sales in Odoo eCommerce by allowing shop owners 
        to configure quantity limits and dynamic pricing tiers for each product. By setting the Min Sale Qty, Max Sale Qty, 
        and Quantity Steps, store administrators can easily restrict the quantity that can be purchased per product. 
        Meanwhile, by leveraging Odoo's pricelist functionality, store owners can create various pricing bands, providing 
        customers with tiered discounts based on the quantity they are purchasing.

        How do I set up quantity limits for products in Odoo eCommerce?
        Can I create different price bands for different quantities in Odoo eCommerce?
        How do I restrict purchases of a product to specific quantities in Odoo?
        Is it possible to display different prices for the same product based on the quantity selected?
        What are the benefits of setting minimum and maximum quantity restrictions for products in Odoo?
        How does Odoo's pricelist functionality help manage volume-based discounts for eCommerce?
        How can I control the quantity of products in the cart in Odoo eCommerce?
        Can I set different product prices for bulk purchases in Odoo eCommerce?
        How can I prevent customers from purchasing more products than available in Odoo?

        Shop Quantity
        Shop Quantity in odoo
        Shop Quantity in website
        Product Pricing Tiers
        Product Pricing Tiers in odoo
        Product Pricing Tiers in website
        Pricelist Adjustment by Quantity
        Pricelist Adjustment by Quantity in odoo
        Pricelist Adjustment by Quantity in website
        Quantity-Based Discounts
        Quantity-Based Discounts in odoo
        Quantity Discounts for eCommerce
        Quantity Discounts for eCommerce in odoo
        Quantity-Based Discounts in website
        Price Tier Configuration for Bulk Orders
        Price Tier Configuration for Bulk Orders in odoo
        Price Tier Configuration for Bulk Orders in website
        Advanced Quantity Restrictions
        Advanced Quantity Restrictions in odoo
        Advanced Quantity Restrictions in website
        Min-Max Quantity Control for Sales
        Min-Max Quantity Control for Sales in odoo
        Min-Max Quantity Control for Sales in website
        """,
    "sequence": 10,
    "description":
        """
        This module adds a more advanced layer of control over product sales in Odoo eCommerce by allowing shop owners 
        to configure quantity limits and dynamic pricing tiers for each product. By setting the Min Sale Qty, Max Sale Qty, 
        and Quantity Steps, store administrators can easily restrict the quantity that can be purchased per product. 
        Meanwhile, by leveraging Odoo's pricelist functionality, store owners can create various pricing bands, providing 
        customers with tiered discounts based on the quantity they are purchasing.

        How do I set up quantity limits for products in Odoo eCommerce?
        Can I create different price bands for different quantities in Odoo eCommerce?
        How do I restrict purchases of a product to specific quantities in Odoo?
        Is it possible to display different prices for the same product based on the quantity selected?
        What are the benefits of setting minimum and maximum quantity restrictions for products in Odoo?
        How does Odoo's pricelist functionality help manage volume-based discounts for eCommerce?
        How can I control the quantity of products in the cart in Odoo eCommerce?
        Can I set different product prices for bulk purchases in Odoo eCommerce?
        How can I prevent customers from purchasing more products than available in Odoo?

        Shop Quantity
        Shop Quantity in odoo
        Shop Quantity in website
        Product Pricing Tiers
        Product Pricing Tiers in odoo
        Product Pricing Tiers in website
        Pricelist Adjustment by Quantity
        Pricelist Adjustment by Quantity in odoo
        Pricelist Adjustment by Quantity in website
        Quantity-Based Discounts
        Quantity-Based Discounts in odoo
        Quantity Discounts for eCommerce
        Quantity Discounts for eCommerce in odoo
        Quantity-Based Discounts in website
        Price Tier Configuration for Bulk Orders
        Price Tier Configuration for Bulk Orders in odoo
        Price Tier Configuration for Bulk Orders in website
        Advanced Quantity Restrictions
        Advanced Quantity Restrictions in odoo
        Advanced Quantity Restrictions in website
        Min-Max Quantity Control for Sales
        Min-Max Quantity Control for Sales in odoo
        Min-Max Quantity Control for Sales in website
        """,
    'category': 'eCommerce',
    "price": 80,
    "currency": "USD",
    "license": "OPL-1",
    'depends': ['base', 'website_sale', 'product'],
    'data': [
        'views/product_template.xml',
        'views/template.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            '/cr_shop_quantity/static/src/js/shop.js',
            '/cr_shop_quantity/static/src/js/product.js'

        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}