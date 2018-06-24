# -*- coding: utf-8 -*-

{
    'name': 'Purchase Price Dimension',
    'description': 'Module that expands the way of calculating the price according to dimensions, for the products of purchase',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'data': [
              'views/import_price_table.xml',
              'views/inherited_product_supplier_info_views.xml',
              'views/inherited_purchase_order_views.xml',
            ],
    'category': 'Purchase',
    'depends': [
                'purchase',
                'sale',
                'import_price_table_wizard',
                'sale_variant_configurator',
                'sale_price_dimension',
                'purchase_variant_configurator',
               ],
    'application': True,
    'installable': True,
}
