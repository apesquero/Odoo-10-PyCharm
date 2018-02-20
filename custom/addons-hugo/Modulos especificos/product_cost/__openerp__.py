# -*- coding: utf-8 -*-
{
    'name': "product_cost",

    'summary': """
        Different ways of calculating the cost.
        """,

    'description': """
        Different ways of calculating the cost.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product', 'product_variants_no_automatic_creation', 'product_attribute_types', 'product_price_cost_base'], #TODO product_attribute_hierarchy needed for default?

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_table_cost_view.xml',
        'views/views.xml',
    ],
    'installable': True,
}
