# -*- coding: utf-8 -*-
{
    'name': "product_cost_supplier",

    'summary': """
        Calculating cost from the first supplier price.
        """,

    'description': """
        Calculating cost from the first supplier price.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product_cost', 'supplier_price'],

    'installable': True,
}
