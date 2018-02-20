# -*- coding: utf-8 -*-
{
    'name': "website_sale_attribute_hierarchy",

    'summary': """
        Allow the website shop to follow the hierarchy.
        """,
    'description': """
        Allow the website shop to follow the hierarchy,
        without taking into account whether the product
        variant exists in the db or not.
        
        This module is compatible (but does not require) the
        modules website_sale_value_image and
        website_sale_range_attribute.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product_attribute_hierarchy', 'website_sale_hook', 'website_sale_range_attribute'], #TODO add 'website_sale_product_variants'?

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    #TODO removing hook to put back 'hierarchy' website_.... to 'standard'
    'uninstall_hook': 'website_sale_attribute_hierarchy_uninstall_hook',
}
