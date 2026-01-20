{
    'name': "City Wise Shipping",
    'version': '18.0',
    'category': 'Sales/Website',
    'summary': 'Configure shipping methods and rates based on city',
    'description': """
        This module allows city-wise shipping configuration for Odoo eCommerce.
        Administrators can set shipping methods and rates for specific cities,
        and these are applied during website checkout based on the delivery address.
    """,
    'depends': ['base', 'delivery', 'website_sale','base_address_extended'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/delivery_carrier_views.xml',
        # 'views/website_sale_templates.xml',
        'views/delivery_price_rule.xml',
'views/city_views.xml',
        'data/delivery_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}