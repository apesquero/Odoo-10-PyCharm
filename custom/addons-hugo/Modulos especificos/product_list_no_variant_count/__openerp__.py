# -*- coding: utf-8 -*-
{
    'name': "product_list_no_variant_count",

    'summary': """
        Removes the variant count from the product template list.
        """,
    'description': """
        Removes the variant count from the product template list.
        
        It is useful to speed up the list when product templates have thousands
        of variants.
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
