# -*- coding: utf-8 -*-

{
    'name': 'Purchase Price Dimension',
    'description': 'Módulo que amplia la forma de cálculo del precio en función de dimensiones, para los productos de compra',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'application': True,
    'data': [
              'wizard/import_price_table.xml',
              'views/inherited_product_supplier_info_views.xml',
              'views/inherited_purchase_order_views.xml',
            ],
    'external_dependencies': {'python': ['xlrd',]},
    'category': 'Purchase',
    'depends': ['purchase', 'sale', 'sale_variant_configurator', 'sale_price_dimension'],
    'application': True,
}
