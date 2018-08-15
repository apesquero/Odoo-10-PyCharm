# -*- coding: utf-8 -*-

{
    'name': 'Stock Price Type',
    'description': 'Module that expands the way of calculating the price according to the dimensions, for the products of sale',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'data': [
        'views/stock_picking_views.xml',
        'views/stock_move_views.xml'],
    'category': 'Warehouse',
    'depends': ['stock',
                'purchase_price_type',
                ],
    'application': True,
    'installable': True,
    'auto_install': True,
}
