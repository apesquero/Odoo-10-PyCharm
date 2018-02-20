# -*- coding: utf-8 -*-
{
    'name': "website_sale_range_attribute",

    'summary': """
        Allows the range attribute to have a input in website_sale shop
        where the client can enter a number.
        """,
    'description': """
        Allows the range attribute to have a input in website_sale shop
        where the client can enter a number.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale_hook', 'product_attribute_types'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
}
