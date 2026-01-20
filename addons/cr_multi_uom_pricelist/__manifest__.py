# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": " Multi UOM Pricelist | Sales Pricelist | Invoice Pricelist",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Sales",
    "summary": """
    This app is used to construct pricelists based on product unit of measure-UOM along with various 
    UOM which product to apply pricelist after that set price for product then use pricelist to Sales order and Invoice.
    Odoo Pricelist by UOM,
    Product UOM Pricelist Odoo App,
    Odoo Sales Pricelist with Unit of Measure,
    Set Product Price by UOM in Odoo,
    Odoo UOM Based Pricing,
    Odoo Pricelist for Multiple Units of Measure,
    Odoo Sales Order Pricelist by UOM,
    Odoo Invoice Pricelist Based on UOM,
    Manage Product Prices by UOM in Odoo,
    Odoo Pricelist Configuration by Unit of Measure,
    How to create a pricelist based on product UOM in Odoo?
    Can Odoo apply different prices for products with multiple units of measure?
    How to use UOM-based pricelists in Odoo sales orders?
    Does Odoo support UOM-specific pricing in invoices?
    How to configure product pricing by unit of measure in Odoo?
    Can I set separate prices for the same product using different UOMs in Odoo?
    How does the UOM-based pricelist improve pricing flexibility in Odoo?
    How to manage multiple UOM pricelists for sales and invoicing in Odoo?
    Can Odoo automatically apply the right UOM pricelist on sales orders?
    What is the benefit of using UOM-based pricelists in Odoo?
    """,
    "license": "OPL-1",
    "version": "19.0.0.1",
    "description": """
    This app is used to construct pricelists based on product unit of measure-UOM along with various 
    UOM which product to apply pricelist after that set price for product then use pricelist to Sales order and Invoice.
    Odoo Pricelist by UOM,
    Product UOM Pricelist Odoo App,
    Odoo Sales Pricelist with Unit of Measure,
    Set Product Price by UOM in Odoo,
    Odoo UOM Based Pricing,
    Odoo Pricelist for Multiple Units of Measure,
    Odoo Sales Order Pricelist by UOM,
    Odoo Invoice Pricelist Based on UOM,
    Manage Product Prices by UOM in Odoo,
    Odoo Pricelist Configuration by Unit of Measure,
    How to create a pricelist based on product UOM in Odoo?
    Can Odoo apply different prices for products with multiple units of measure?
    How to use UOM-based pricelists in Odoo sales orders?
    Does Odoo support UOM-specific pricing in invoices?
    How to configure product pricing by unit of measure in Odoo?
    Can I set separate prices for the same product using different UOMs in Odoo?
    How does the UOM-based pricelist improve pricing flexibility in Odoo?
    How to manage multiple UOM pricelists for sales and invoicing in Odoo?
    Can Odoo automatically apply the right UOM pricelist on sales orders?
    What is the benefit of using UOM-based pricelists in Odoo?
    """,
    "depends": ["sale_management", "stock"],
    "application": True,
    'data': [
        'views/account.xml',
        'views/product_pricelist.xml'
    ],

    "auto_install": False,
    "installable": True,
    "images": ["static/description/banner.png", ],
    "price": 23,
    "currency": "EUR"
}
