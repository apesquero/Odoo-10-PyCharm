# -*- coding: utf-8 -*-

{
    'name': 'Sale Price Dimension',
    'description': 'Module that expands the way of calculating the price according to the dimensions, for the products of sale',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'data': [ 'security/ir.model.access.csv',
              'views/import_price_table.xml',
              'views/inherited_product_product_views.xml',
              'views/inherited_product_template_views.xml',
              'views/inherited_sale_order_views.xml',
            ],
    'demo': ['data/product.template.csv'],
    'category': 'Sales',
    'depends': ['sale', 'sale_variant_configurator', 'import_price_table_wizard',],
    'application': True,
    'installable': True,
}
