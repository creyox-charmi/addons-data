{
    'name': 'Website Header Effects',
    'version': '16.0.0.0',
    'summary': 'Adds a fade-out effect to the website header',
    'category': 'Website',
    'author': 'Your Name or Company',
    'website': 'https://yourcompany.com',
    'depends': ['website'],
    'data': [
        'views/website_header.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'header/static/src/scss/header_style.scss',
'header/static/src/js/custom_header/header.js',
        ],
# 'web.assets_frontend_minimal': [
#             'header/static/src/js/custom_header/header.js',
#         ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
