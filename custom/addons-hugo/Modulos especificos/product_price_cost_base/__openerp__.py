# -*- coding: utf-8 -*-
{
    'name': "product_price_cost_base",
    
    'summary': """
        Base module for shared methods between product_list_price and product_cost. It does nothing on its own.
        """,
    
    'description': """
        Base module for shared methods between product_list_price and product_cost. It does nothing on its own.
    """,
    
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    
    # any module necessary for this one to work correctly
    'depends': ['product', 'product_variants_no_automatic_creation', 'product_attribute_types'],
    
    'installable': True,
}
