# -*- coding: utf-8 -*-
{
    'name': "product_list_price_bom",

    'summary': """
        Calculating price list from bom.
        """,

    'description': """
        Calculating price list from bom.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product_list_price', 'mrp_product_variants_types'],

    'installable': True,
}
