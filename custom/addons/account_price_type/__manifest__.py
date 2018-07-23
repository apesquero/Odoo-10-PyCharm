# -*- coding: utf-8 -*-

{
    'name': 'Account Price Type',
    'description': 'Module that expands the way of calculating the price according to the dimensions, for the products of sale',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'data': [
             'views/account_invoice_view.xml',
             ],
    'category': 'Accounting',
    'depends': ['account',
                'account_variant_configurator',
                'product_price_type',
                ],
    'application': True,
    'installable': True,
}
