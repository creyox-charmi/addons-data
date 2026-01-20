# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Stock Inter Transfer Account | Inter-Warehouse Transfer Account | Internal Stock Transfer Account | Inventory Transfer Tracking Account",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0.0.1",
    "summary":
        """
        The Stock Inter transfer Account for Odoo facilitates advanced and customizable
        accounting for stock movements, particularly for internal stock transfers between
        different locations. This enhancement supports multi-company environments and
        provides an easy way to handle inventory valuation and accounting for storable
        products, even with different stock locations. It introduces new functionalities for
        tracking journal entries and stock accounts based on the location of the inventory,
        allowing companies to define specific accounts, and stock journals per location. Key
        to this enhancement is the ability to automatically generate journal entries for
        internal stock transfers between different locations, ensuring that each transaction
        is accurately reflected in the company's accounting system.The Stock Accounting
        Enhancement for Odoo significantly improves stock management, accounting automation,
        and flexibility, particularly for businesses managing multiple storage locations.
        
        Stock Inter Transfer Account
        Stock Inter Transfer Account in odoo
        Inter-Warehouse Transfer Account
        Inter-Warehouse Transfer Account in odoo
        Internal Stock Transfer Account
        Internal Stock Transfer Account in odoo
        Inventory Transfer Tracking Account
        Inventory Transfer Tracking Account in odoo
        Stock Relocation Account
        Stock Relocation Account in odoo
        Stock Allocation Transfer Account
        Stock Allocation Transfer Account in odoo
        Internal Inventory Transfer Register
        Internal Inventory Transfer Register in odoo
        Stock Exchange Account
        Stock Exchange Account in odoo
        Warehouse Transfer Register
        Warehouse Transfer Register in odoo
        """,
    "sequence": 10,
    "description":
        """
        The Stock Inter transfer Account for Odoo facilitates advanced and customizable
        accounting for stock movements, particularly for internal stock transfers between
        different locations. This enhancement supports multi-company environments and
        provides an easy way to handle inventory valuation and accounting for storable
        products, even with different stock locations. It introduces new functionalities for
        tracking journal entries and stock accounts based on the location of the inventory,
        allowing companies to define specific accounts, and stock journals per location. Key
        to this enhancement is the ability to automatically generate journal entries for
        internal stock transfers between different locations, ensuring that each transaction
        is accurately reflected in the company's accounting system.The Stock Accounting
        Enhancement for Odoo significantly improves stock management, accounting automation,
        and flexibility, particularly for businesses managing multiple storage locations.
        
        Stock Inter Transfer Account
        Stock Inter Transfer Account in odoo
        Inter-Warehouse Transfer Account
        Inter-Warehouse Transfer Account in odoo
        Internal Stock Transfer Account
        Internal Stock Transfer Account in odoo
        Inventory Transfer Tracking Account
        Inventory Transfer Tracking Account in odoo
        Stock Relocation Account
        Stock Relocation Account in odoo
        Stock Allocation Transfer Account
        Stock Allocation Transfer Account in odoo
        Internal Inventory Transfer Register
        Internal Inventory Transfer Register in odoo
        Stock Exchange Account
        Stock Exchange Account in odoo
        Warehouse Transfer Register
        Warehouse Transfer Register in odoo
        """,
    "category": "Warehouse",
    "price": 80,
    "currency": "USD",
    "license": "OPL-1",
    "depends": ["base", "stock", "account"],
    "data": [
        "views/res_config_settings.xml",
        "views/stock_location.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
