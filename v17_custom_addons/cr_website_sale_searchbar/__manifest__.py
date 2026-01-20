# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Advance Searchbar',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "17.0",
    'summary':
        """

        """,
    "sequence": 10,
    "description":
        """

        """,
    'category': 'website',
    "price": '',
    "currency": "USD",
    "license": "OPL-1",
    'depends': ['base','website' ,'website_sale', 'product','portal','rating',],
    'data': [
        'views/res_config_settings.xml'
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         '/cr_shop_quantity/static/src/js/shop.js',
    #         '/cr_shop_quantity/static/src/js/product.js'
    #     ],
    # },
# 'assets': {
#         'web.assets_frontend': [
#             'cr_website_sale_searchbar/static/src/xml/portal_chatter.xml',
#         ],
#     },
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
