# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Stock Summary Report",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "17.0.0.1",
    "summary":
        """

        """,
    "sequence": 10,
    "description":
        """

        """,
    "category": "Warehouse",
    "price": "29",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "stock", ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/stock_summary.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
