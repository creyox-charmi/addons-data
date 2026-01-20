# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Warehouse Stock Restrictions | Inventory Access Control | Warehouse Access Management | Stock Management Restrictions | Warehouse Access Control",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "summary": """
        This module is design for managing access and security in complex inventory systems.
        By limiting which users can view or interact with specific warehouses , locations ,
        Immediate and Planned Transfer , And You can also limit the number of sale order and
        sale warehouses , also restrict buttons like Return , Scrap , Unlock , and add
        validation on create record for specific user. An administrator assigns specific 
        warehouses and stock locations to users. The assigned warehouses and locations become 
        visible only to the assigned users, limiting their ability to interact with other 
        parts of the warehouse. This setup ensures that users can only work with their 
        designated areas, preventing unauthorized access to other user's stock or locations. 
        This module is particularly useful in multi-warehouse or multi-location environments 
        where different users need to access only certain areas of the business operations.

        Warehouse Stock Restrictions
        Warehouse Stock Restrictions in Odoo
        Inventory Access Control
        Inventory Access Control in Odoo
        Warehouse Access Management
        Warehouse Access Management in Odoo
        Stock Management Restrictions
        Stock Management Restrictions in Odoo
        Stock Allocation Control
        Stock Allocation Control in Odoo
        Warehouse Access Restrictions
        Warehouse Access Restrictions in Odoo
        Warehouse Access Control
        Warehouse Access Control in Odoo
        Warehouse Inventory Limits
        Warehouse Inventory Limits in Odoo
        Warehouse Access Limits
        Warehouse Access Limits in Odoo
        """,
    "version": "16.0.0.1",
    "sequence": 10,
    "description": """
        This module is design for managing access and security in complex inventory systems.
        By limiting which users can view or interact with specific warehouses , locations ,
        Immediate and Planned Transfer , And You can also limit the number of sale order and
        sale warehouses , also restrict buttons like Return , Scrap , Unlock , and add
        validation on create record for specific user. An administrator assigns specific 
        warehouses and stock locations to users. The assigned warehouses and locations become 
        visible only to the assigned users, limiting their ability to interact with other 
        parts of the warehouse. This setup ensures that users can only work with their 
        designated areas, preventing unauthorized access to other user's stock or locations. 
        This module is particularly useful in multi-warehouse or multi-location environments 
        where different users need to access only certain areas of the business operations.
        
        Warehouse Stock Restrictions
        Warehouse Stock Restrictions in Odoo
        Inventory Access Control
        Inventory Access Control in Odoo
        Warehouse Access Management
        Warehouse Access Management in Odoo
        Stock Management Restrictions
        Stock Management Restrictions in Odoo
        Stock Allocation Control
        Stock Allocation Control in Odoo
        Warehouse Access Restrictions
        Warehouse Access Restrictions in Odoo
        Warehouse Access Control
        Warehouse Access Control in Odoo
        Warehouse Inventory Limits
        Warehouse Inventory Limits in Odoo
        Warehouse Access Limits
        Warehouse Access Limits in Odoo
        """,
    "category": "Warehouse",
    "price": "99",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "stock", "mrp", "sale", "web"],
    "data": [
        "security/cr_access_restrict_warehouses.xml",
        "views/stock_picking_type.xml",
        "views/res_users.xml",
        "views/stock_picking.xml",
        "views/mrp_production.xml",
        "views/stock_location.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
