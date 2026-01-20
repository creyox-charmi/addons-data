# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Bulk Quantity Enforcer for Odoo | Odoo Bulk Order Quantity Tool | Odoo Multi-Website Quantity Control | E-Commerce Quantity Multiplier Module",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "summary": """
      The "Website Multiple of Quantity" module for Odoo allows eCommerce platforms to enforce product purchases 
      in specific multiples, such as dozens or sets of 10. It provides configurable rules for each product and supports 
      multi-website functionality. Features include customizing product views, managing cart items with predefined 
      quantities, and handling multiple quantities in sales orders. This is useful for businesses selling products in 
      bulk or predefined units. 

    Bulk Quantity Enforcer for Odoo
    Odoo Multiple of Quantity Manager
    E-Commerce Quantity Multiplier Module
    Custom Purchase Multiples for Odoo
    Odoo Bulk Order Quantity Tool
    Website Product Quantity Restriction
    Odoo Multiples-Only Purchase App
    Fixed Quantity Purchases for Odoo
    E-Commerce Bulk Product Manager
    Product Purchase Multiples Configuration
    Set Purchase Multiples in Odoo
    Odoo Multi-Website Quantity Control
    Quantity Multiplier Plugin for Odoo
    Bulk Product Selector for Odoo
    Odoo Sales Order Quantity Rules
    Enforce Quantity Multiples in Odoo
    Odoo E-Commerce Bulk Order Manager
    Product Units Manager for Odoo Websites
    Odoo Shopping Cart Quantity Validator
    Fixed Quantity Shopping App for Odoo
    How can I enforce bulk order rules on my Odoo eCommerce site?
    Can I restrict product purchases to multiples of a specific quantity in Odoo?
    What module helps set fixed purchase multiples for products in Odoo?
    Is there a way to sell products in sets or packs on Odoo websites?
    How do I manage quantity restrictions for eCommerce orders in Odoo?
    Which Odoo module supports bulk quantity shopping rules?
    Can Odoo enforce buying products in batches?
    How do I implement a "buy in multiples" feature in Odoo?
    Which module helps configure bulk order quantities for Odoo sales?
    How to customize purchase quantities for specific products in Odoo?
    What’s the best Odoo module for managing multi-website product quantities?
    How can I ensure customers purchase predefined quantities in Odoo?
    Is there an Odoo tool for enforcing minimum and multiple purchase quantities?
    What app supports bulk product sales for Odoo websites?
    How do I set up cart quantity validation for Odoo eCommerce?
    Can I customize product quantity options on my Odoo website?
    How do I restrict purchases to specific packs or cases in Odoo?
    What module handles bulk purchase rules for multi-website Odoo setups?
    How do I set fixed sales quantities in Odoo's eCommerce platform?
    Is there a plugin for Odoo that enables selling in fixed multiples?

    """,
    "license": "OPL-1",
    "version": "18.0",
    "sequence": 10,
    "description": """
         The "Website Multiple of Quantity" module for Odoo allows eCommerce platforms to enforce product purchases 
      in specific multiples, such as dozens or sets of 10. It provides configurable rules for each product and supports 
      multi-website functionality. Features include customizing product views, managing cart items with predefined 
      quantities, and handling multiple quantities in sales orders. This is useful for businesses selling products in 
      bulk or predefined units. 

    Bulk Quantity Enforcer for Odoo
    Odoo Multiple of Quantity Manager
    E-Commerce Quantity Multiplier Module
    Custom Purchase Multiples for Odoo
    Odoo Bulk Order Quantity Tool
    Website Product Quantity Restriction
    Odoo Multiples-Only Purchase App
    Fixed Quantity Purchases for Odoo
    E-Commerce Bulk Product Manager
    Product Purchase Multiples Configuration
    Set Purchase Multiples in Odoo
    Odoo Multi-Website Quantity Control
    Quantity Multiplier Plugin for Odoo
    Bulk Product Selector for Odoo
    Odoo Sales Order Quantity Rules
    Enforce Quantity Multiples in Odoo
    Odoo E-Commerce Bulk Order Manager
    Product Units Manager for Odoo Websites
    Odoo Shopping Cart Quantity Validator
    Fixed Quantity Shopping App for Odoo
    How can I enforce bulk order rules on my Odoo eCommerce site?
    Can I restrict product purchases to multiples of a specific quantity in Odoo?
    What module helps set fixed purchase multiples for products in Odoo?
    Is there a way to sell products in sets or packs on Odoo websites?
    How do I manage quantity restrictions for eCommerce orders in Odoo?
    Which Odoo module supports bulk quantity shopping rules?
    Can Odoo enforce buying products in batches?
    How do I implement a "buy in multiples" feature in Odoo?
    Which module helps configure bulk order quantities for Odoo sales?
    How to customize purchase quantities for specific products in Odoo?
    What’s the best Odoo module for managing multi-website product quantities?
    How can I ensure customers purchase predefined quantities in Odoo?
    Is there an Odoo tool for enforcing minimum and multiple purchase quantities?
    What app supports bulk product sales for Odoo websites?
    How do I set up cart quantity validation for Odoo eCommerce?
    Can I customize product quantity options on my Odoo website?
    How do I restrict purchases to specific packs or cases in Odoo?
    What module handles bulk purchase rules for multi-website Odoo setups?
    How do I set fixed sales quantities in Odoo's eCommerce platform?
    Is there a plugin for Odoo that enables selling in fixed multiples?
    """,
    "category": "eCommerce",
    "website": "www.creyox.com",
    "depends": ["base", "sale", "product", "website_sale", 'website', 'web'],
    "data": [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/quantity_setter.xml',
        'views/setting_config_website.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'cr_multiple_quantity_set_on_product/static/src/js/ProductQuantityComponent.js',
            'cr_multiple_quantity_set_on_product/static/src/js/quantity_buttons/*',
            'cr_multiple_quantity_set_on_product/static/src/js/product/*',
        ],

    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
    "price": 25,
    "currency": "USD",
}
