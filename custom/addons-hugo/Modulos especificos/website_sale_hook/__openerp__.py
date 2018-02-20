# -*- coding: utf-8 -*-
{
    'name': "website_sale_hook",

    'summary': """
        Hooks on website_sale for other modules to use.
        """,
    'description': """
        Hooks on website_sale for other modules to use.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
