# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": " Multi UOM Pricelist | Sales Pricelist | Invoice Pricelist",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Sales",
    "summary": "This app is used to construct pricelists based on product unit of measure-UOM along with various UOM which product to apply pricelist after that set price for product then use pricelist to Sales order and Invoice.",
    "description": """This app is used to construct pricelists based on product unit of measure-UOM along with various UOM which product to apply pricelist after that set price for product then use pricelist to Sales order and Invoice.""",
    "license": "LGPL-3",
    "version": "18.0",
    "depends": ["sale_management", "stock"],
    "application": True,
    "data": ["views/account.xml", "views/product_pricelist.xml"],
    "auto_install": False,
    "installable": True,
    "images": ["static/description/banner.png"],
    "price": 23,
    "currency": "EUR",
}
