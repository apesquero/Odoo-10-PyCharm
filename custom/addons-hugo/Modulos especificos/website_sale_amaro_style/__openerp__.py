# -*- coding: utf-8 -*-
{
    'name': "Website Sale Amaro Style",

    'summary': """
        Website Sale Amaro Style""",

    'description': """
        Website Sale Amaro Style
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale_hook', 'website_sale_attribute_hierarchy'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
}
