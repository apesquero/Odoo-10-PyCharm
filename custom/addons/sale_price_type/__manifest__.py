# -*- coding: utf-8 -*-

{
    'name': 'Sale Price Type',
    'description': 'Module that expands the way of calculating the price according to the dimensions, for the products of sale',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'data': [
             'views/sale_order_views.xml',
             'menu/product_fabric_menu.xml',
             ],
    'category': 'Sales',
    'depends': ['sale',
                'sale_variant_configurator',
                'product_price_type',
                'account_price_type',
                ],
    'application': True,
    'installable': True,
}
