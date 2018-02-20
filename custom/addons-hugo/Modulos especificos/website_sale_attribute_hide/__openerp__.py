# -*- coding: utf-8 -*-
{
    'name': "website_sale_attribute_hide",

    'summary': """
        Creates new types of website_sale attribute types,
        that completely hide when there is only one option enabled.
        """,
    'description': """
        Creates new types of website_sale attribute types,
        that completely hide when there is only one option enabled.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product', 'website_sale_hook', 'website_sale_value_image_hook'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
}
