# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Stock Picking Cancel Reverse | Inventory Movement Reversal | Stock Picking Reset To Draft",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "summary":
        """
            The Stock Picking Cancel Odoo app provides a solution for cancel validated or completed stock pickings and 
            revert them to a draft stage. Users often encounter situations where mistakes occur during the receipt of stock or 
            delivery of goods, especially regarding quantities or other details. In standard Odoo, there is no built-in 
            option to revert these actions. This app addresses that gap, allowing users to effectively cancel validated 
            delivery orders and incoming shipments.
            Stock Picking Cancle Reverse
            Stock Picking Cancle Reverse in odoo
            Inventory Movement Reversal
            Inventory Movement Reversal in odoo
            Stock Picking Reset To Draft
            Stock Picking Reset To Draft in odoo
            Stock Allocation Cancelation
            Stock Allocation Cancelation in odoo
            Stock Adjustment and Reversion
            Stock Adjustment and Reversion in odoo
            Inventory Transfer Reversal
            Inventory Transfer Reversal in odoo
            Shipment Cancellation Restore
            Shipment Cancellation Restore in odoo
            Delivery Cancellation Revert
            Delivery Cancellation Revert in odoo
            Picking Process Reset
            Picking Process Reset in odoo
        """,
    "version": "16.0.0.1",
    "sequence": 10,
    "description":
        """
            The Stock Picking Cancel Odoo app provides a solution for reverting validated or completed stock pickings 
            back to a draft stage. Users often encounter situations where mistakes occur during the receipt of stock or 
            delivery of goods, especially regarding quantities or other details. In standard Odoo, there is no built-in 
            option to revert these actions. This app addresses that gap, allowing users to effectively cancel validated 
            delivery orders and incoming shipments.
            Stock Picking Cancle Reverse
            Stock Picking Cancle Reverse in odoo
            Inventory Movement Reversal
            Inventory Movement Reversal in odoo
            Reset To Draft in Stock Picking
            Reset To Draft in Stock Picking in odoo
            Stock Allocation Cancelation
            Stock Allocation Cancelation in odoo
            Stock Adjustment and Reversion
            Stock Adjustment and Reversion in odoo
            Inventory Transfer Reversal
            Inventory Transfer Reversal in odoo
            Shipment Cancellation Restore
            Shipment Cancellation Restore in odoo
            Delivery Cancellation Revert
            Delivery Cancellation Revert in odoo
            Picking Process Reset
            Picking Process Reset in odoo
        """
    ,
    "category": "Warehouse",
    "price": "",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "stock"],
    "data": [
        "security/button_rights.xml",
        "views/stock_picking.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
