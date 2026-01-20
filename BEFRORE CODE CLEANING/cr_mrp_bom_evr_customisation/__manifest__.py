{
    "name": "MRP BOM EVR Customisation",
    "summary": "Custom enhancements for MRP BOM and EVR processes",
    "version": "18.0.0.0",
    "category": "Manufacturing",
    "license": "LGPL-3",
    "author": "Your Company",
    "website": "https://yourcompany.com",
    "depends": [
        'mrp', 'project', 'purchase', 'stock', 'purchase_stock', 'purchase_mrp', 'bizzup_product_customisation',
        'mrp_plm',
        "cr_mrp_bom_customisation",
    ],
    "data": [
        "security/ir.model.access.csv",
        'views/mrp_bom_line_branch_views.xml',
        "views/stock_location_views.xml",
        "data/stock_location_data.xml",
        "views/purchase_order_view.xml",
        "views/mrp_bom_line_view.xml",
        "views/mrp_production.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'cr_mrp_bom_evr_customisation/static/src/**/*',
        ],
    },
    'post_init_hook': 'post_init_hook',
    "installable": True,
    "application": False,
    "auto_install": False,
}
