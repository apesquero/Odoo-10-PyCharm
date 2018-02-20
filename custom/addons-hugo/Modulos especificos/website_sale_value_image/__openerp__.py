# -*- coding: utf-8 -*-
{
    'name': "website_sale_value_image",

    'summary': """
        Allow the website shop to show the attribute value image.
        """,
    'description': """
        Allow the website shop to show the attribute value image.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale', 'product_attribute_value_image'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'installable': False,
}
