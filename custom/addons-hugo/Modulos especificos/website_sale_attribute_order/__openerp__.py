# -*- coding: utf-8 -*-
{
    'name': "website_sale_attribute_order",

    'summary': """
        Makes the website shop follow the attribute order selected.
        """,
    'description': """
        Makes the website shop follow the attribute order selected.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product_attribute_order_base', 'website_sale_hook'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    "auto_install": True,
}
