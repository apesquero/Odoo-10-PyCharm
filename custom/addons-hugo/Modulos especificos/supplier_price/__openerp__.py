# -*- coding: utf-8 -*-
{
    'name': "supplier_price",

    'summary': """
        Different ways of calculating the supplier price.
        """,

    'description': """
        Different ways of calculating the supplier price.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product',
                'product_attribute_types',
                'purchase',
                'purchase_product_variants',
                'purchase_product_variants_types',
                'stock',
                'mrp',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_table_supplier_price_view.xml',
        'views/views.xml',
    ],
    'installable': True,
}
