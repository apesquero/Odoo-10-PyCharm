# -*- coding: utf-8 -*-
{
    'name': "product_attribute_order_base",

    'summary': """
        More options to stablish attribute order.
        """,
    'description': """
        More options to stablish attribute order, for example
        following the order in the attribute lines of a product
        and not the standard attribute one.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'installable': True,
}
