# -*- coding: utf-8 -*-
{
    'name': "Mrp BoM eval",

    'summary': """
        Allows quantity and range attributes custom value in the
        Bill of Materials to be calculated instead of only a
        fixed numeric value.""",

    'description': """
        Allows quantity and range attributes custom value in the
        Bill of Materials to be calculated instead of only a
        fixed numeric value.
        
        You can introduce a formula in the Product Quantity field,
        that accepts numbers, basic operands and a very limited set
        of functions. It also admits the name of an attribute of
        the product to produce if
        the attribute is of type range or numeric, and it will
        substitute the name for the value of the attribute for the
        calculations. The name of the attribute should switch spaces
        for an underscore, so f.e. an attribute named 'Main Height'
        should be written as 'Main_Height'.
        
        Same applies for range attributes custom values.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'mrp_product_variants', 'mrp_product_variants_types'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'post_init_hook': 'init_assign_qty',
}
