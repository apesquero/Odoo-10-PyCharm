# -*- coding: utf-8 -*-
{
    'name': "website_sale_variant_topdown",

    'summary': """
        Product variants exhibit a topdown behaviour in the website shop.
        """,
    'description': """
        This module assumes a top down hierarchy in the attributes of a product
        (see product_attribute_hierarchy module) and always calculates the options
        of the lower attributes based on the choices of the above ones. It hides the
        options that are not available, so the user can never chose a invalid
        combination.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale_hook', 'product'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'installable': False,
}
