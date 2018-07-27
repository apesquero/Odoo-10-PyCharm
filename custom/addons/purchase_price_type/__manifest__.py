# -*- coding: utf-8 -*-

{
    'name': 'Purchase Price Type',
    'description': 'Module that expands the way of calculating the price according to dimensions, for the products of purchase',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'data': [
             'views/import_price_table.xml',
             'views/product_supplier_info_views.xml',
             'views/purchase_order_views.xml',
             ],
    'category': 'Purchase',
    'depends': [
                'purchase',
                'purchase_variant_configurator',
                'product_price_type',
               ],
    'application': True,
    'installable': True,
}
