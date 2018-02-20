# -*- coding: utf-8 -*-
{
    'name': "purchase_uom_grouping",

    'summary': """
        Option in product description to allow or disallow the purchase
        module to group the quantities of the same product.
        
        Not compatible with module purchase_requisition.
        """,

    'description': """
        Allow or disallow grouping of quantities of the same product.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'product'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'installable': True,
}
