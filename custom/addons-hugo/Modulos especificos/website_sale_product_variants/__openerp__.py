# -*- coding: utf-8 -*-
{
    'name': "website_sale_product_variants",

    'summary': """
        Allow the website shop buy by product_template_id
        and attributes, instead of only by product_id.
        """,
    'description': """
        Allow the website shop buy by product_template_id
        and attributes, instead of needed the product_id,
        the same way sale_product_variants does for the 
        internal sale menu.
        
        Also, it makes website_sale and sale_product_variants
        compatible. I has no direct dependency with
        website_sale_attribute_hierarchy, but that module will
        not be able to buy stuff without this one installed.
        """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_product_variants', 'website_sale'], #website_sale_hook?

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
}
