# -*- coding: utf-8 -*-

{
    'name': 'Sale Price Dimension',
    'description': 'Módulo que amplia la forma de cálculo del precio en función de dimensiones, para los productos de venta',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'application': True,
    'data': [
              'wizard/import_price_table.xml',
              'views/inherited_product_product_views.xml',
              'views/inherited_product_template_views.xml',
              'views/inherited_sale_order_views.xml',
            ],
    'external_dependencies': {'python': ['xlrd',]},
    'qweb': ['static/src/xml/*.xml'],
    'category': 'Sales',
    'depends': ['sale', 'sale_variant_configurator'],
    'application': True,
}
